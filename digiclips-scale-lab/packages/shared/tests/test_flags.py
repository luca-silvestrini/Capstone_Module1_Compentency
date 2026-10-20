from shared.flags import Flag, FlagStore


def test_disabled_flag_is_off_for_everyone():
    f = Flag("x", enabled=False, rollout_percent=100, allow_roles=("admin",))
    assert not f.is_on("u1", "admin")


def test_rollout_is_deterministic():
    f = Flag("resumable_uploads", True, 25)
    assert all(f.is_on("user-42") == f.is_on("user-42") for _ in range(10))


def test_rollout_only_grows():
    users = [f"user-{i}" for i in range(2000)]
    on_at = {p: {u for u in users if Flag("f", True, p).is_on(u)} for p in (10, 25, 50, 100)}
    assert on_at[10] <= on_at[25] <= on_at[50] <= on_at[100]
    assert len(on_at[100]) == 2000


def test_rollout_percentage_is_roughly_right():
    users = [f"user-{i}" for i in range(5000)]
    share = sum(Flag("f", True, 25).is_on(u) for u in users) / len(users)
    assert 0.22 < share < 0.28


def test_role_override_and_unknown_flag_fails_closed():
    store = FlagStore({"beta": Flag("beta", True, 0, ("admin",))})
    assert store.is_on("beta", "anyone", role="admin")
    assert not store.is_on("beta", "anyone")
    assert not store.is_on("does_not_exist", "anyone")
