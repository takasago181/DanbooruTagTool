#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}: {count}\n--- needle ---\n{old[:1000]}")
    path.write_text(text.replace(old, new), encoding="utf-8")


xaml = ROOT / "src/DanbooruTagTool.App/MainWindow.xaml"
code = ROOT / "src/DanbooruTagTool.App/MainWindow.xaml.cs"
vm = ROOT / "src/DanbooruTagTool.App/ViewModels/MainViewModel.cs"
tests = ROOT / "src/DanbooruTagTool.Tests/Issue76MainUiIntegrationTests.cs"

replace_once(
    xaml,
    'SelectedItemChanged="NavigationChanged" Background="Transparent"',
    'SelectedItemChanged="NavigationChanged" Expanded="NavigationNodeExpanded" Collapsed="NavigationNodeCollapsed" Background="Transparent"',
)

replace_once(
    xaml,
    '<DockPanel Margin="0,0,0,2"><TextBlock Text="追加で絞り込み" Style="{StaticResource HintText}" FontWeight="SemiBold" VerticalAlignment="Center"/><Button DockPanel.Dock="Right" Content="すべて解除" Command="{Binding ClearSpecialFacets}" Style="{StaticResource CompactButton}" Padding="8,3" MinHeight="25" Margin="8,0,0,0"/></DockPanel>',
    '<Grid Margin="0,0,0,2"><Grid.ColumnDefinitions><ColumnDefinition Width="*"/><ColumnDefinition Width="Auto"/></Grid.ColumnDefinitions><TextBlock Text="追加で絞り込み" Style="{StaticResource HintText}" FontWeight="SemiBold" VerticalAlignment="Center"/><StackPanel Grid.Column="1" Orientation="Horizontal" HorizontalAlignment="Right"><Button Content="1つ戻す" Command="{Binding UndoSpecialFacet}" Style="{StaticResource CompactButton}" Padding="7,3" MinHeight="25" Width="82" Margin="8,0,4,0"/><Button Content="全解除" Command="{Binding ClearSpecialFacets}" Style="{StaticResource CompactButton}" Padding="7,3" MinHeight="25" Width="68" Margin="0"/></StackPanel></Grid>',
)

replace_once(
    code,
    'Loaded += (_, _) => { vm.UpdateChipLanguage(); FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(vm.RestoreScroll); SyncNavigationSelection(); };',
    'Loaded += (_, _) => { vm.UpdateChipLanguage(); FindChild<ScrollViewer>(DictionaryList)?.ScrollToVerticalOffset(vm.RestoreScroll); SyncNavigationSelection(); ExpandFixedSpecialGroups(); };',
)

replace_once(
    code,
    '    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e) { if (!syncingNavigation && e.NewValue is NavigationNode node) vm.Navigate.Execute(node); }\n',
    '''    private void NavigationChanged(object sender, RoutedPropertyChangedEventArgs<object> e)\n    {\n        if (syncingNavigation || e.NewValue is not NavigationNode node) return;\n        if (IsFixedSpecialGroup(node))\n        {\n            Dispatcher.BeginInvoke(SyncNavigationSelection, DispatcherPriority.Loaded);\n            return;\n        }\n        vm.Navigate.Execute(node);\n    }\n    private static bool IsFixedSpecialGroup(NavigationNode node) => node.Key is "special-v2:kinds" or "special-v2:body" or "special-v2:themes";\n    private void NavigationNodeExpanded(object sender, RoutedEventArgs e)\n    {\n        if (e.OriginalSource is TreeViewItem item && item.Header is NavigationNode node && node.Key == "special")\n            Dispatcher.BeginInvoke(ExpandFixedSpecialGroups, DispatcherPriority.Loaded);\n    }\n    private void NavigationNodeCollapsed(object sender, RoutedEventArgs e)\n    {\n        if (e.OriginalSource is not TreeViewItem item || item.Header is not NavigationNode node || !IsFixedSpecialGroup(node)) return;\n        e.Handled = true;\n        Dispatcher.BeginInvoke(() => item.IsExpanded = true, DispatcherPriority.Loaded);\n    }\n    private void ExpandFixedSpecialGroups()\n    {\n        var special = vm.Navigation.FirstOrDefault(node => node.Key == "special");\n        if (special == null) return;\n        var root = NavigationTree.ItemContainerGenerator.ContainerFromItem(special) as TreeViewItem;\n        if (root?.IsExpanded != true) return;\n        root.UpdateLayout();\n        foreach (var group in special.Children.Where(IsFixedSpecialGroup))\n        {\n            var item = root.ItemContainerGenerator.ContainerFromItem(group) as TreeViewItem;\n            if (item == null) { root.UpdateLayout(); item = root.ItemContainerGenerator.ContainerFromItem(group) as TreeViewItem; }\n            if (item != null) item.IsExpanded = true;\n        }\n    }\n''',
)

replace_once(
    vm,
    '    private SpecialBrowseV2Filter specialFilter = SpecialBrowseV2Filter.Empty;\n',
    '    private SpecialBrowseV2Filter specialFilter = SpecialBrowseV2Filter.Empty;\n    private readonly Stack<SpecialBrowseV2Filter> specialFilterHistory = new();\n',
)

replace_once(
    vm,
    '    public RelayCommand ToggleSpecialFacet { get; }\n    public RelayCommand ClearSpecialFacets { get; }\n',
    '    public RelayCommand ToggleSpecialFacet { get; }\n    public RelayCommand UndoSpecialFacet { get; }\n    public RelayCommand ClearSpecialFacets { get; }\n',
)

replace_once(
    vm,
    '        Navigate = Normal(p => { if (p is NavigationNode n) NavigateTo(n.Key); });\n',
    '        Navigate = Normal(p => { if (p is NavigationNode n && !IsSpecialAxisHeading(n.Key)) NavigateTo(n.Key); });\n',
)

replace_once(
    vm,
    '''        ToggleSpecialFacet = Normal(p =>\n        {\n            if (specialBrowse == null || p is not SpecialBrowseFacetOptionViewModel option) return;\n            specialFilter = option.Axis switch\n            {\n                SpecialBrowseV2Axis.Kind => specialFilter.WithKind(specialFilter.KindId == option.Id ? null : option.Id),\n                SpecialBrowseV2Axis.BodySite => specialFilter.ToggleBodySite(option.Id),\n                SpecialBrowseV2Axis.Theme => specialFilter.ToggleTheme(option.Id),\n                _ => specialFilter\n            };\n            RefreshResults(); Persist();\n        }, p => specialBrowse != null && p is SpecialBrowseFacetOptionViewModel);\n        ClearSpecialFacets = Normal(_ =>\n        {\n            if (specialBrowse == null) return;\n            specialFilter = SpecialBrowseV2Filter.Empty;\n            browse = "special";\n            Notify(nameof(BrowseKey));\n            RefreshResults(); Persist();\n        }, _ => specialBrowse != null && !specialFilter.IsEmpty);\n''',
    '''        ToggleSpecialFacet = Normal(p =>\n        {\n            if (specialBrowse == null || p is not SpecialBrowseFacetOptionViewModel option) return;\n            var next = option.Axis switch\n            {\n                SpecialBrowseV2Axis.Kind => specialFilter.WithKind(specialFilter.KindId == option.Id ? null : option.Id),\n                SpecialBrowseV2Axis.BodySite => specialFilter.ToggleBodySite(option.Id),\n                SpecialBrowseV2Axis.Theme => specialFilter.ToggleTheme(option.Id),\n                _ => specialFilter\n            };\n            ApplySpecialFilter(next, remember: true);\n            RefreshResults(); Persist();\n        }, p => specialBrowse != null && p is SpecialBrowseFacetOptionViewModel);\n        UndoSpecialFacet = Normal(_ =>\n        {\n            if (specialBrowse == null || specialFilter.IsEmpty) return;\n            if (specialFilterHistory.TryPop(out var previous)) specialFilter = previous;\n            else if (specialFilter.ThemeIds.Count > 0) specialFilter = specialFilter.ToggleTheme(specialFilter.ThemeIds.Last());\n            else if (specialFilter.BodySiteIds.Count > 0) specialFilter = specialFilter.ToggleBodySite(specialFilter.BodySiteIds.Last());\n            else specialFilter = specialFilter.WithKind(null);\n            if (specialFilter.IsEmpty) { browse = "special"; Notify(nameof(BrowseKey)); }\n            RefreshResults(); Persist();\n        }, _ => specialBrowse != null && !specialFilter.IsEmpty);\n        ClearSpecialFacets = Normal(_ =>\n        {\n            if (specialBrowse == null) return;\n            specialFilterHistory.Clear();\n            specialFilter = SpecialBrowseV2Filter.Empty;\n            browse = "special";\n            Notify(nameof(BrowseKey));\n            RefreshResults(); Persist();\n        }, _ => specialBrowse != null && !specialFilter.IsEmpty);\n''',
)

replace_once(
    vm,
    '    private static SpecialBrowseV2Filter SpecialFilterFromBrowse(string key)\n',
    '''    private static bool IsSpecialAxisHeading(string key) => key is "special-v2:kinds" or "special-v2:body" or "special-v2:themes";\n    private static bool SameSpecialFilter(SpecialBrowseV2Filter left, SpecialBrowseV2Filter right) =>\n        left.KindId == right.KindId && left.BodySiteIds.SetEquals(right.BodySiteIds) && left.ThemeIds.SetEquals(right.ThemeIds);\n    private void ApplySpecialFilter(SpecialBrowseV2Filter next, bool remember)\n    {\n        if (SameSpecialFilter(next, specialFilter)) return;\n        if (remember) specialFilterHistory.Push(specialFilter);\n        specialFilter = next;\n    }\n    private static SpecialBrowseV2Filter SpecialFilterFromBrowse(string key)\n''',
)

replace_once(
    vm,
    '        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, InspectEntry, Navigate, Back, ClearQuery, ToggleSpecialFacet, ClearSpecialFacets, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets, NewPreset, ApplyPreset, CopyPresetNegative, CapturePresetPositive, SavePreset, DeletePreset, OpenForgeSettings, SaveForgeSettings }) command.Refresh();\n',
    '        foreach (var command in new[] { Copy, Import, New, Recover, Undo, Redo, Delete, DeleteOne, Inspect, InspectEntry, Navigate, Back, ClearQuery, ToggleSpecialFacet, UndoSpecialFacet, ClearSpecialFacets, FindPrevious, FindNextCommand, OpenEditor, StartDirect, ApplyDirect, CancelDirect, ApplyWeight, OpenPresets, NewPreset, ApplyPreset, CopyPresetNegative, CapturePresetPositive, SavePreset, DeletePreset, OpenForgeSettings, SaveForgeSettings }) command.Refresh();\n',
)

replace_once(
    vm,
    '        ClearSpecialFacets.Refresh();\n',
    '        UndoSpecialFacet.Refresh(); ClearSpecialFacets.Refresh();\n',
)

replace_once(
    vm,
    '''        browse = key;\n        if (specialBrowse != null)\n        {\n            specialFilter = key.StartsWith("special-v2:", StringComparison.Ordinal) ? SpecialFilterFromBrowse(key)\n                : key == "special" ? SpecialBrowseV2Filter.Empty\n                : key.StartsWith("general", StringComparison.Ordinal) ? SpecialBrowseV2Filter.Empty : specialFilter;\n        }\n''',
    '''        browse = key;\n        if (specialBrowse != null)\n        {\n            if (key.StartsWith("special-v2:kind:", StringComparison.Ordinal) || key.StartsWith("special-v2:body:", StringComparison.Ordinal) || key.StartsWith("special-v2:theme:", StringComparison.Ordinal))\n                ApplySpecialFilter(SpecialFilterFromBrowse(key), remember);\n            else if (key == "special" || key.StartsWith("general", StringComparison.Ordinal))\n            {\n                if (remember) specialFilterHistory.Clear();\n                specialFilter = SpecialBrowseV2Filter.Empty;\n            }\n        }\n''',
)

insert = '''\n    [Fact]\n    public void One_step_back_removes_only_the_latest_special_filter_condition()\n    {\n        var vm = Vm();\n        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");\n        vm.ToggleSpecialFacet.Execute(vm.SpecialBodyOptions.Single(option => option.Id == "MOUTH_ORAL"));\n        vm.ToggleSpecialFacet.Execute(vm.SpecialThemeOptions.Single(option => option.Id == "BDSM_RESTRAINT"));\n\n        vm.UndoSpecialFacet.Execute(null);\n        Assert.Equal("道具・物 × 口・口内", vm.BrowseLabel);\n        Assert.True(vm.HasSpecialFacets);\n\n        vm.UndoSpecialFacet.Execute(null);\n        Assert.Equal("道具・物", vm.BrowseLabel);\n\n        vm.UndoSpecialFacet.Execute(null);\n        Assert.Equal("special", vm.BrowseKey);\n        Assert.False(vm.HasSpecialFacets);\n    }\n\n    [Fact]\n    public void Fixed_special_axis_headings_do_not_replace_the_active_leaf_filter()\n    {\n        var vm = Vm();\n        vm.NavigateTo("special-v2:kind:TOOL_OBJECT");\n        var special = Assert.Single(vm.Navigation, node => node.Key == "special");\n        var heading = Assert.Single(special.Children, node => node.Key == "special-v2:body");\n\n        vm.Navigate.Execute(heading);\n\n        Assert.Equal("special-v2:kind:TOOL_OBJECT", vm.BrowseKey);\n        Assert.Equal("道具・物", vm.BrowseLabel);\n    }\n'''
replace_once(
    tests,
    '\n    [Fact]\n    public void Persisted_old_special_path_is_migrated_to_v2_root_without_touching_prompt_state()\n',
    insert + '\n    [Fact]\n    public void Persisted_old_special_path_is_migrated_to_v2_root_without_touching_prompt_state()\n',
)

print("Issue #76 browse control refinement applied")
