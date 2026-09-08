# R3 full pytest capture

- verdict: `ENVIRONMENT_BLOCKED`
- setup errors: `52`
- call failures: `0`
- exception types: `{'BaseException': 52, 'PermissionError': 52, 'WinError': 52}`
- root causes: `{'WINDOWS_ACL_TEMP_SETUP': 52}`

## First three setup errors

### 1. `tests/test_generation_profile.py::test_absent_empty_and_unknown_profile_are_left_joins`

```text
cls = <class '_pytest.runner.CallInfo'>
func = <function call_and_report.<locals>.<lambda> at 0x00000273FE2C7100>
when = 'setup'
reraise = (<class '_pytest.outcomes.Exit'>, <class 'KeyboardInterrupt'>)

    @classmethod
    def from_call(
        cls,
        func: Callable[[], TResult],
        when: Literal["collect", "setup", "call", "teardown"],
        reraise: type[BaseException] | tuple[type[BaseException], ...] | None = None,
    ) -> CallInfo[TResult]:
        """Call func, wrapping the result in a CallInfo.

        :param func:
            The function to call. Called without arguments.
        :type func: Callable[[], _pytest.runner.TResult]
        :param when:
            The phase in which the function is called.
        :param reraise:
            Exception or exceptions that shall propagate if raised by the
            function, instead of being wrapped in the CallInfo.
        """
        excinfo = None
        instant = timing.Instant()
        try:
>           result: TResult | None = func()
                                     ^^^^^^

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:344:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:246: in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\logging.py:843: in pytest_runtest_setup
    yield
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\capture.py:895: in pytest_runtest_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:164: in pytest_runtest_setup
    item.session._setupstate.setup(item)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:514: in setup
    col.setup()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\python.py:1674: in setup
    self._request._fillfixtures()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:720: in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:549: in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:640: in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1128: in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\setuponly.py:36: in pytest_fixture_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1196: in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:923: in call_fixture_func
    fixture_result = next(generator)
                     ^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:264: in tmp_path
    path = _mk_tmp(request, tmp_path_factory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:251: in _mk_tmp
    return factory.mktemp(name, numbered=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:135: in mktemp
    p = make_numbered_dir(root=self.getbasetemp(), prefix=basename, mode=0o700)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:229: in make_numbered_dir
    max_existing = max(map(parse_num, find_suffixes(root, prefix)), default=-1)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:188: in extract_suffixes
    for entry in iter:
                 ^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

root = WindowsPath('C:/Codex/DanbooruTagTool/.pytest-r3-audit-final2')
prefix = 'test_absent_empty_and_unknown_'

    def find_prefixed(root: Path, prefix: str) -> Iterator[os.DirEntry[str]]:
        """Find all elements in root that begin with the prefix, case-insensitive."""
        l_prefix = prefix.lower()
>       for x in os.scandir(root):
                 ^^^^^^^^^^^^^^^^
E       PermissionError: [WinError 5] アクセスが拒否されました。: 'C:\\Codex\\DanbooruTagTool\\.pytest-r3-audit-final2'

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:176: PermissionError
```

### 2. `tests/test_generation_profile.py::test_malformed_profiles_rejected[change0]`

```text
cls = <class '_pytest.runner.CallInfo'>
func = <function call_and_report.<locals>.<lambda> at 0x000002739E4C4B80>
when = 'setup'
reraise = (<class '_pytest.outcomes.Exit'>, <class 'KeyboardInterrupt'>)

    @classmethod
    def from_call(
        cls,
        func: Callable[[], TResult],
        when: Literal["collect", "setup", "call", "teardown"],
        reraise: type[BaseException] | tuple[type[BaseException], ...] | None = None,
    ) -> CallInfo[TResult]:
        """Call func, wrapping the result in a CallInfo.

        :param func:
            The function to call. Called without arguments.
        :type func: Callable[[], _pytest.runner.TResult]
        :param when:
            The phase in which the function is called.
        :param reraise:
            Exception or exceptions that shall propagate if raised by the
            function, instead of being wrapped in the CallInfo.
        """
        excinfo = None
        instant = timing.Instant()
        try:
>           result: TResult | None = func()
                                     ^^^^^^

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:344:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:246: in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\logging.py:843: in pytest_runtest_setup
    yield
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\capture.py:895: in pytest_runtest_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:164: in pytest_runtest_setup
    item.session._setupstate.setup(item)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:514: in setup
    col.setup()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\python.py:1674: in setup
    self._request._fillfixtures()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:720: in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:549: in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:640: in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1128: in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\setuponly.py:36: in pytest_fixture_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1196: in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:923: in call_fixture_func
    fixture_result = next(generator)
                     ^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:264: in tmp_path
    path = _mk_tmp(request, tmp_path_factory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:251: in _mk_tmp
    return factory.mktemp(name, numbered=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:135: in mktemp
    p = make_numbered_dir(root=self.getbasetemp(), prefix=basename, mode=0o700)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:229: in make_numbered_dir
    max_existing = max(map(parse_num, find_suffixes(root, prefix)), default=-1)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:188: in extract_suffixes
    for entry in iter:
                 ^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

root = WindowsPath('C:/Codex/DanbooruTagTool/.pytest-r3-audit-final2')
prefix = 'test_malformed_profiles_reject'

    def find_prefixed(root: Path, prefix: str) -> Iterator[os.DirEntry[str]]:
        """Find all elements in root that begin with the prefix, case-insensitive."""
        l_prefix = prefix.lower()
>       for x in os.scandir(root):
                 ^^^^^^^^^^^^^^^^
E       PermissionError: [WinError 5] アクセスが拒否されました。: 'C:\\Codex\\DanbooruTagTool\\.pytest-r3-audit-final2'

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:176: PermissionError
```

### 3. `tests/test_generation_profile.py::test_malformed_profiles_rejected[change1]`

```text
cls = <class '_pytest.runner.CallInfo'>
func = <function call_and_report.<locals>.<lambda> at 0x000002739E4C6340>
when = 'setup'
reraise = (<class '_pytest.outcomes.Exit'>, <class 'KeyboardInterrupt'>)

    @classmethod
    def from_call(
        cls,
        func: Callable[[], TResult],
        when: Literal["collect", "setup", "call", "teardown"],
        reraise: type[BaseException] | tuple[type[BaseException], ...] | None = None,
    ) -> CallInfo[TResult]:
        """Call func, wrapping the result in a CallInfo.

        :param func:
            The function to call. Called without arguments.
        :type func: Callable[[], _pytest.runner.TResult]
        :param when:
            The phase in which the function is called.
        :param reraise:
            Exception or exceptions that shall propagate if raised by the
            function, instead of being wrapped in the CallInfo.
        """
        excinfo = None
        instant = timing.Instant()
        try:
>           result: TResult | None = func()
                                     ^^^^^^

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:344:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:246: in <lambda>
    lambda: runtest_hook(item=item, **kwds), when=when, reraise=reraise
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\logging.py:843: in pytest_runtest_setup
    yield
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\capture.py:895: in pytest_runtest_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:164: in pytest_runtest_setup
    item.session._setupstate.setup(item)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\runner.py:514: in setup
    col.setup()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\python.py:1674: in setup
    self._request._fillfixtures()
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:720: in _fillfixtures
    item.funcargs[argname] = self.getfixturevalue(argname)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:549: in getfixturevalue
    fixturedef = self._get_active_fixturedef(argname)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:640: in _get_active_fixturedef
    fixturedef.execute(request=subrequest)
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1128: in execute
    result = ihook.pytest_fixture_setup(fixturedef=self, request=request)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_hooks.py:512: in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\pluggy\_manager.py:120: in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\setuponly.py:36: in pytest_fixture_setup
    return (yield)
            ^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:1196: in pytest_fixture_setup
    result = call_fixture_func(fixturefunc, request, kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\fixtures.py:923: in call_fixture_func
    fixture_result = next(generator)
                     ^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:264: in tmp_path
    path = _mk_tmp(request, tmp_path_factory)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:251: in _mk_tmp
    return factory.mktemp(name, numbered=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\tmpdir.py:135: in mktemp
    p = make_numbered_dir(root=self.getbasetemp(), prefix=basename, mode=0o700)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:229: in make_numbered_dir
    max_existing = max(map(parse_num, find_suffixes(root, prefix)), default=-1)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:188: in extract_suffixes
    for entry in iter:
                 ^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

root = WindowsPath('C:/Codex/DanbooruTagTool/.pytest-r3-audit-final2')
prefix = 'test_malformed_profiles_reject'

    def find_prefixed(root: Path, prefix: str) -> Iterator[os.DirEntry[str]]:
        """Find all elements in root that begin with the prefix, case-insensitive."""
        l_prefix = prefix.lower()
>       for x in os.scandir(root):
                 ^^^^^^^^^^^^^^^^
E       PermissionError: [WinError 5] アクセスが拒否されました。: 'C:\\Codex\\DanbooruTagTool\\.pytest-r3-audit-final2'

C:\Users\takas\AppData\Local\Python\pythoncore-3.12-64\Lib\site-packages\_pytest\pathlib.py:176: PermissionError
```

## All failed phases

The complete records are in `full_pytest_report.json`.

- `setup` `tests/test_generation_profile.py::test_absent_empty_and_unknown_profile_are_left_joins`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_malformed_profiles_rejected[change0]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_malformed_profiles_rejected[change1]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_malformed_profiles_rejected[change2]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_malformed_profiles_rejected[change3]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_malformed_profiles_rejected[change4]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_audit_only_semantic_promotion_is_rejected`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_profile_columns_duplicates_and_tag_drift_rejected`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_family_and_observation_validation`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_v2_metadata_does_not_change_fixture_statistics[192]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_v2_metadata_does_not_change_fixture_statistics[1578]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_generation_profile.py::test_v2_metadata_does_not_change_fixture_statistics[1117]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_ruleset2_integration.py::test_model_aux_local_source_rules_and_final_gate`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[none]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[missing]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[size]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[hash]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[directory]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage0_integrity.py::test_protected_check_rejects_missing_modified_and_unexpected_sources[extra]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change0]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change1]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change2]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change3]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change4]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change5]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_rejects_invalid_rows[change6]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_semantic_duplicate_and_multiple_candidates`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage3_knowledge.py::test_loaders_reject_corruption`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage5_runtime_index.py::test_true_one_two_three_and_five_and_post_ids`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage5_runtime_index.py::test_empty_and_unknown_tag_handling`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage5_runtime_index.py::test_candidate_aggregation_input_exclusion_and_global_counts`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage5_runtime_index.py::test_snapshot_mismatch_and_corruption_are_rejected`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage5_runtime_index.py::test_manifest_snapshot_mixing_and_hash_corruption_are_rejected`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage6_recommendations.py::test_raw_statistics_and_core_and_runtime_only_exclusion`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage6_recommendations.py::test_drop_one_and_combination_specificity`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage6_recommendations.py::test_alias_logical_merge_deduplicates_and_semantic_is_never_candidate`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8a_semantics.py::test_semantic_loader_rejects_invalid_role_and_duplicate_canonical`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8a_semantics.py::test_hint_loader_rejects_invalid_enums[role-SUBJECT_BASIC-NOT_A_ROLE-invalid semantic role]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8a_semantics.py::test_hint_loader_rejects_invalid_enums[bucket-,common,-,sometimes,-invalid bucket]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8a_semantics.py::test_hint_loader_rejects_invalid_enums[kind-,CORE_BASIS,-,NOT_A_KIND,-invalid hint kind]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[special_id-999999-unknown special_id]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[candidate_canonical-not_a_real_canonical-unknown candidate canonical]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[support_slot-NOT_A_SLOT-invalid support_slot]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[support_class-NOT_A_CLASS-invalid support_class]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[intent_axis-NOT_AN_AXIS-invalid intent_axis]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[intent_direction-SIDEWAYS-invalid intent_direction]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_special_profile_loader_rejects_invalid_identity_and_enums[combination_mode-MAGICAL-invalid combination_mode]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_enabled_row_requires_support_class_and_duplicate_is_error`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_observed_evidence_requires_test_profile_and_model_scope[MODEL_OBSERVED]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_observed_evidence_requires_test_profile_and_model_scope[USER_ENV_VERIFIED]`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_disabled_row_is_loaded_for_audit_but_hidden_at_runtime`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
- `setup` `tests/test_stage8b_support.py::test_family_loader_requires_existing_stage6_family`: `WINDOWS_ACL_TEMP_SETUP` / `['BaseException', 'PermissionError', 'WinError']`
