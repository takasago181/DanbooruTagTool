from array import array

from tools.stage2_benchmark import aggregate_bidir, aggregate_forward, and_posts, build


POSTS = [
    (10, ["a", "b", "c"]), (11, ["a", "b"]), (12, ["a", "c"]),
    (13, ["b", "c"]), (14, ["a", "b", "c", "d"]), (15, ["d"]),
]


def test_true_and_and_all_candidate_counts_match_between_architectures():
    forward = build(POSTS, bidirectional=False)
    bidirectional = build(POSTS, bidirectional=True)
    query = ["a", "b", "c"]

    expected_base = array("I", [0, 4])
    assert and_posts(forward, query) == expected_base
    assert and_posts(bidirectional, query) == expected_base

    selected = {forward["names"][tag] for tag in query}
    assert aggregate_forward(forward, expected_base, selected) == {forward["names"]["d"]: 1}
    selected_bidir = {bidirectional["names"][tag] for tag in query}
    assert aggregate_bidir(bidirectional, expected_base, selected_bidir) == {
        bidirectional["names"]["d"]: 1
    }
