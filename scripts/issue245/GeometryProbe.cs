using System.IO;
using System.Text.Json;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;
using DanbooruTagTool.App;
using DanbooruTagTool.App.ViewModels;
using DanbooruTagTool.Core;
using DanbooruTagTool.Data;

// Independent reproduction of #223's initial native Show / group selection,
// plus an explicit content-layout experiment. No Application/startup, audit renderer,
// file-backed UserData, network, OS changes or production mutation.
internal static class GeometryProbe
{
    [STAThread]
    public static void Main(string[] args)
    {
        if (args.Length != 3) throw new ArgumentException("GeometryProbe <authority-root> <new-json-output> <source-revision>");
        var output = Path.GetFullPath(args[1]); if (File.Exists(output)) throw new IOException("Refuse evidence overwrite");
        Directory.CreateDirectory(Path.GetDirectoryName(output)!);
        var entries = Issue70CatalogOverlayImporter.Read(Path.Combine(args[0], Issue70CatalogOverlayImporter.RelativePath));
        entries = Issue216BrowseHomeImporter.Apply(Path.Combine(args[0], Issue216BrowseHomeImporter.RelativePath), entries);
        entries = Issue223BrowseGroupImporter.Apply(Path.Combine(args[0], Issue223BrowseGroupImporter.GroupsPath), Path.Combine(args[0], Issue223BrowseGroupImporter.MembersPath), entries);
        var catalog = new Catalog(entries); var cases = new List<object>();
        foreach (var requested in new[] { (1200, 900), (1500, 900), (900, 560), (1280, 720) })
        {
            var vm = new MainViewModel(catalog, new ProbeStore(), new ProbeClipboard());
            var w = new MainWindow(vm) { Width = requested.Item1, Height = requested.Item2, WindowState = WindowState.Normal, ShowInTaskbar = false };
            w.Show(); vm.Dictionary.OpenRelated(catalog.Resolve("fire_emblem")!); Pump(w.Dispatcher); w.UpdateLayout();
            var view = (FrameworkElement)w.FindName("DictionaryWorkspace");
            var buttons = Children<Button>(view).Where(b => b.DataContext is DictionaryWorkspaceViewModel.GroupOption).ToArray();
            var chosen = buttons.Single(b => ((DictionaryWorkspaceViewModel.GroupOption)b.DataContext).Id == "fire_emblem:_three_houses");
            chosen.Command!.Execute(chosen.CommandParameter); Pump(w.Dispatcher); w.UpdateLayout();
            var list = Children<ListBox>(view).Single(l => l.Name == "DictionaryList");
            cases.Add(Snapshot("native", w, list, requested, vm.Results.Count));
            // Keep Window ancestor bindings intact; explicit content size tests the
            // requested client layout without claiming that native chrome has resized.
            var content = (FrameworkElement)w.Content;
            content.Width = requested.Item1 - 16; content.Height = requested.Item2 - 39;
            w.UpdateLayout(); Pump(w.Dispatcher); w.UpdateLayout();
            cases.Add(Snapshot("explicit-content", w, list, requested, vm.Results.Count));
            w.Close();
        }
        File.WriteAllText(output, JsonSerializer.Serialize(new { Revision = args[2], AuthorityRoot = args[0], Session = System.Diagnostics.Process.GetCurrentProcess().SessionId,
            Screen = new { SystemParameters.PrimaryScreenWidth, SystemParameters.PrimaryScreenHeight, SystemParameters.VirtualScreenWidth, SystemParameters.VirtualScreenHeight, WorkArea = RectValues(SystemParameters.WorkArea) }, Cases = cases }, new JsonSerializerOptions { WriteIndented = true }));
    }
    private static object Snapshot(string mode, Window w, ListBox list, (int,int) requested, int resultCount)
    {
        var dpi = VisualTreeHelper.GetDpi(w); var parents = new List<object>();
        for (DependencyObject? p = list; p is not null; p = VisualTreeHelper.GetParent(p))
            if (p is FrameworkElement e) parents.Add(new { Type = e.GetType().Name, e.Name, Width = e.ActualWidth, Height = e.ActualHeight, DesiredWidth = e.DesiredSize.Width, DesiredHeight = e.DesiredSize.Height,
                Rows = e is Grid g ? g.RowDefinitions.Select(r => r.ActualHeight).ToArray() : null });
        var root = (FrameworkElement)w.Content;
        var controls = Children<FrameworkElement>(root).Where(e => e is TabControl || e is Border && e.Style == w.Resources["HeaderCard"])
            .Select(e => new { Type = e.GetType().Name, e.Name, Width = e.ActualWidth, Height = e.ActualHeight, Y = e.TranslatePoint(new Point(), root).Y }).ToArray();
        return new { Mode = mode, RequestedWidth = requested.Item1, RequestedHeight = requested.Item2, WidthProperty = w.Width, HeightProperty = w.Height, NativeActualWidth = w.ActualWidth, NativeActualHeight = w.ActualHeight,
            State = w.WindowState.ToString(), DpiX = dpi.PixelsPerInchX, DpiY = dpi.PixelsPerInchY, DpiScale = dpi.DpiScaleX, DictionaryListHeight = list.ActualHeight, OriginalHeightAssertion = list.ActualHeight > 80, ResultCount = resultCount, Parents = parents, HeaderAndTabs = controls };
    }
    private static object RectValues(Rect r) => new { r.X, r.Y, r.Width, r.Height };
    private static IEnumerable<T> Children<T>(DependencyObject root) where T : DependencyObject
    { for (var i=0;i<VisualTreeHelper.GetChildrenCount(root);i++) { var c=VisualTreeHelper.GetChild(root,i); if(c is T t)yield return t; foreach(var d in Children<T>(c))yield return d; } }
    private static void Pump(Dispatcher d)
    { var frame=new DispatcherFrame(); var timer=new DispatcherTimer(DispatcherPriority.Background,d){Interval=TimeSpan.FromMilliseconds(75)}; timer.Tick+=(_,_)=>{timer.Stop();frame.Continue=false;};timer.Start();Dispatcher.PushFrame(frame); }
    private sealed class ProbeStore : IUserStateStore { private UserState? state; public UserState? Load()=>state;public void Save(UserState s)=>state=s; }
    private sealed class ProbeClipboard : IClipboardService { public string Read()=>"";public void Write(string value){} }
}
