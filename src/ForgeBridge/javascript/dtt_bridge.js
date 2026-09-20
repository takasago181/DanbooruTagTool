(() => {
  "use strict";

  const selectors = {
    positive: ["#txt2img_prompt textarea", "textarea#txt2img_prompt", 'textarea[aria-label="Prompt"]'],
    negative: ["#txt2img_neg_prompt textarea", "textarea#txt2img_neg_prompt", 'textarea[aria-label="Negative prompt"]'],
    generate: ["button#txt2img_generate", "#txt2img_generate button", "#txt2img_generate"],
    seed: "#txt2img_seed",
    steps: "#txt2img_steps",
    sampler: "#txt2img_sampling",
    scheduler: "#txt2img_scheduler",
    cfg: "#txt2img_cfg_scale",
    width: "#txt2img_width",
    height: "#txt2img_height",
    checkpoint: ".model_selection"
  };
  const protocolVersion = 1;
  const bootedAt = Date.now();
  const sessionKey = "dtt-bridge-last-request-id";
  let polling = false;

  function findInput(selectorsToTry) {
    for (const selector of selectorsToTry) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLTextAreaElement || element instanceof HTMLInputElement) return element;
    }
    return null;
  }

  function findClickable(selectorsToTry) {
    for (const selector of selectorsToTry) {
      const element = document.querySelector(selector);
      if (element instanceof HTMLElement) return element;
    }
    return null;
  }

  function inputInside(selector) {
    const root = document.querySelector(selector);
    if (root instanceof HTMLInputElement || root instanceof HTMLTextAreaElement) return root;
    return root?.querySelector("input:not([type='hidden']), textarea") ?? null;
  }

  function setValue(element, value) {
    const prototype = element instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
    if (!descriptor || typeof descriptor.set !== "function") throw new Error("value_setter_missing");
    descriptor.set.call(element, String(value));
    if (typeof updateInput === "function") updateInput(element);
    else element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function nextFrame() {
    return new Promise(resolve => window.requestAnimationFrame(() => resolve()));
  }

  function sleep(milliseconds) {
    return new Promise(resolve => window.setTimeout(resolve, milliseconds));
  }

  function fail(code) {
    const error = new Error(code);
    error.dttCode = code;
    throw error;
  }

  function setScalar(selector, value, errorCode) {
    const input = inputInside(selector);
    if (!(input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement)) fail(errorCode);
    setValue(input, value);
  }

  function normalized(value) {
    return String(value ?? "").trim().toLowerCase();
  }

  async function setChoice(selector, value, errorCode, bestEffort = false) {
    const root = document.querySelector(selector);
    if (!(root instanceof HTMLElement)) {
      if (bestEffort) return false;
      fail(errorCode);
    }

    const wanted = normalized(value);
    const radios = [...root.querySelectorAll("input[type='radio']")];
    for (const radio of radios) {
      const label = radio.closest("label") ?? root.querySelector(`label[for="${radio.id}"]`);
      const text = normalized(label?.textContent ?? radio.value);
      if (normalized(radio.value) === wanted || text === wanted) {
        radio.click();
        await nextFrame();
        return true;
      }
    }

    const input = root.querySelector("input:not([type='hidden'])");
    if (input instanceof HTMLInputElement) {
      input.focus();
      input.click();
      setValue(input, value);
      await sleep(60);

      const options = [...document.querySelectorAll("[role='option']")]
        .filter(option => option instanceof HTMLElement && option.offsetParent !== null);
      const exact = options.find(option => normalized(option.textContent) === wanted);
      if (exact instanceof HTMLElement) {
        exact.click();
        await nextFrame();
        return true;
      }

      input.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", code: "Enter", bubbles: true }));
      input.dispatchEvent(new KeyboardEvent("keyup", { key: "Enter", code: "Enter", bubbles: true }));
      await nextFrame();
      if (normalized(input.value) === wanted) return true;
    }

    if (bestEffort) return false;
    fail(errorCode);
  }

  async function applyRecipe(payload) {
    if (payload.serverError) fail(payload.serverError);
    const settings = payload.settings;
    if (!settings || typeof settings !== "object") return;

    if (settings.seed !== undefined) setScalar(selectors.seed, settings.seed, "seed_missing");
    if (settings.steps !== undefined) setScalar(selectors.steps, settings.steps, "steps_missing");
    if (settings.cfg !== undefined) setScalar(selectors.cfg, settings.cfg, "cfg_missing");
    if (settings.width !== undefined) setScalar(selectors.width, settings.width, "width_missing");
    if (settings.height !== undefined) setScalar(selectors.height, settings.height, "height_missing");
    if (typeof settings.sampler === "string") await setChoice(selectors.sampler, settings.sampler, "sampler_missing");
    if (typeof settings.scheduler === "string") await setChoice(selectors.scheduler, settings.scheduler, "scheduler_missing");

    // Neo can finish the checkpoint refresh asynchronously after the bridge
    // has already published the pending item. Give the Gradio controls a
    // short settle window before a recipe Generate click.
    if (typeof payload.appliedModel === "string") await sleep(3000);

    // The Python companion applies the checkpoint before publishing the
    // pending item. Do not touch Forge's checkpoint dropdown here: Neo may
    // refresh the Gradio page while it reconciles that control, which would
    // tear down this JavaScript context before the ACK is posted.

    await nextFrame();
    await nextFrame();
  }

  async function report(requestId, success, error = "") {
    try {
      await fetch("/dtt-bridge/result", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ protocolVersion, requestId, success, error })
      });
    } catch (_) {
      // The desktop client will time out if the acknowledgement cannot be sent.
    }
  }

  async function handle(payload) {
    const requestId = payload.requestId;
    const generate = payload.action === "send_and_generate";
    const applyOnly = payload.action === "apply_recipe";
    const needsAck = generate || applyOnly;

    const positive = findInput(selectors.positive);
    if (!positive || typeof payload.positive !== "string") {
      if (needsAck) await report(requestId, false, "positive_missing");
      return;
    }

    try {
      setValue(positive, payload.positive);

      if (payload.negativeMode === "replace") {
        const negative = findInput(selectors.negative);
        if (!negative || typeof payload.negative !== "string") {
          if (needsAck) await report(requestId, false, "negative_missing");
          return;
        }
        setValue(negative, payload.negative);
      }

      if (payload.settings) await applyRecipe(payload);

      if (generate) {
        const button = findClickable(selectors.generate);
        if (!button) {
          await report(requestId, false, "generate_missing");
          return;
        }
        // A Generate click may refresh the Gradio tree immediately. Publish
        // the accepted action before that click so the browser context cannot
        // lose the ACK while Forge starts the job.
        await report(requestId, true, "");
        await nextFrame();
        await nextFrame();
        button.click();
      } else if (applyOnly) {
        await report(requestId, true, "");
      }

      sessionStorage.setItem(sessionKey, requestId);
    } catch (error) {
      if (needsAck) {
        const code = typeof error?.dttCode === "string" ? error.dttCode : (generate ? "generate_failed" : "recipe_failed");
        await report(requestId, false, code);
      }
    }
  }

  async function poll() {
    if (polling) return;
    polling = true;
    try {
      const response = await fetch("/dtt-bridge/pending", { cache: "no-store" });
      if (!response.ok) return;
      const envelope = await response.json();
      const payload = envelope.pending;
      if (envelope.protocolVersion !== protocolVersion || !payload) return;
      if (typeof payload.requestId !== "string" || payload.createdAt < bootedAt) return;
      if (sessionStorage.getItem(sessionKey) === payload.requestId) return;
      await handle(payload);
    } catch (_) {
      // Forge may be starting up; the next short poll will retry health-free.
    } finally {
      polling = false;
    }
  }

  window.setInterval(poll, 700);
  window.setTimeout(poll, 250);
})();
