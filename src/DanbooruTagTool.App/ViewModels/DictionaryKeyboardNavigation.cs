using System.Windows.Input;

namespace DanbooruTagTool.App.ViewModels;

public enum DictionaryKeyboardActionKind
{
    None,
    Move,
    Home,
    End,
    Inspect
}

public readonly record struct DictionaryKeyboardAction(DictionaryKeyboardActionKind Kind, int Offset = 0);

/// <summary>
/// Pure key mapping shared by the Dictionary view and regression tests. The
/// selected EntryViewModel remains owned by DictionaryWorkspaceViewModel.
/// </summary>
public static class DictionaryKeyboardNavigation
{
    public static DictionaryKeyboardAction Resolve(Key key, int columnCount)
    {
        if (columnCount is < 1 or > 2) throw new ArgumentOutOfRangeException(nameof(columnCount));
        return key switch
        {
            Key.Left when columnCount == 2 => new(DictionaryKeyboardActionKind.Move, -1),
            Key.Right when columnCount == 2 => new(DictionaryKeyboardActionKind.Move, 1),
            Key.Up => new(DictionaryKeyboardActionKind.Move, -columnCount),
            Key.Down => new(DictionaryKeyboardActionKind.Move, columnCount),
            Key.PageUp => new(DictionaryKeyboardActionKind.Move, -10 * columnCount),
            Key.PageDown => new(DictionaryKeyboardActionKind.Move, 10 * columnCount),
            Key.Home => new(DictionaryKeyboardActionKind.Home),
            Key.End => new(DictionaryKeyboardActionKind.End),
            Key.Enter => new(DictionaryKeyboardActionKind.Inspect),
            _ => new(DictionaryKeyboardActionKind.None)
        };
    }
}
