using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;

namespace DanbooruTagTool.App.ViewModels;
public class Observable : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;
    protected void Notify([CallerMemberName] string? name = null) => PropertyChanged?.Invoke(this, new(name));
    protected bool Set<T>(ref T field, T value, [CallerMemberName] string? name = null)
    { if (EqualityComparer<T>.Default.Equals(field, value)) return false; field = value; Notify(name); return true; }
}
public sealed class RelayCommand(Action<object?> execute, Predicate<object?>? canExecute = null) : ICommand
{
    public bool CanExecute(object? parameter) => canExecute?.Invoke(parameter) ?? true;
    public void Execute(object? parameter) => execute(parameter);
    public event EventHandler? CanExecuteChanged;
    public void Refresh() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
public sealed class AsyncRelayCommand(Func<object?, Task> execute, Predicate<object?>? canExecute = null) : ICommand
{
    private bool running;
    public bool CanExecute(object? parameter) => !running && (canExecute?.Invoke(parameter) ?? true);
    public async void Execute(object? parameter)
    {
        if (!CanExecute(parameter)) return;
        running = true; Refresh();
        try { await execute(parameter); }
        finally { running = false; Refresh(); }
    }
    public async Task ExecuteAsync(object? parameter)
    {
        if (!CanExecute(parameter)) return;
        running = true; Refresh();
        try { await execute(parameter); }
        finally { running = false; Refresh(); }
    }
    public event EventHandler? CanExecuteChanged;
    public void Refresh() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
