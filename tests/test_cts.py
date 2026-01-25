"""Tests for cipher trapdoor sets."""

import pytest
from cts import (
    HashValue,
    BernoulliBoolean,
    Trapdoor,
    TrapdoorFactory,
    BooleanSet,
    compose_and,
    compose_or,
    compose_not,
    mutual_information,
)


class TestHashValue:
    def test_create_from_bytes(self):
        h = HashValue(b'\x00\x01\x02\x03')
        assert len(h) == 4
        assert h.hex() == "00010203"

    def test_create_from_hex(self):
        h = HashValue.from_hex("deadbeef")
        assert h.data == b'\xde\xad\xbe\xef'

    def test_xor(self):
        a = HashValue(b'\xff\x00')
        b = HashValue(b'\x0f\xf0')
        c = a ^ b
        assert c.data == b'\xf0\xf0'

    def test_and(self):
        a = HashValue(b'\xff\x0f')
        b = HashValue(b'\x0f\xff')
        c = a & b
        assert c.data == b'\x0f\x0f'

    def test_or(self):
        a = HashValue(b'\xf0\x00')
        b = HashValue(b'\x0f\x00')
        c = a | b
        assert c.data == b'\xff\x00'

    def test_not(self):
        a = HashValue(b'\x00\xff')
        b = ~a
        assert b.data == b'\xff\x00'

    def test_length_mismatch_raises(self):
        a = HashValue(b'\x00\x01')
        b = HashValue(b'\x00\x01\x02')
        with pytest.raises(ValueError):
            _ = a ^ b


class TestBernoulliBoolean:
    def test_create_with_rates(self):
        av = BernoulliBoolean(True, alpha=0.1, beta=0.05)
        assert av.value is True
        assert av.alpha == 0.1
        assert av.beta == 0.05

    def test_confidence(self):
        av = BernoulliBoolean(True, alpha=0.1, beta=0.1)
        assert av.confidence == pytest.approx(0.8)

    def test_bool_conversion(self):
        assert bool(BernoulliBoolean(True, alpha=0.5))
        assert not bool(BernoulliBoolean(False, alpha=0.5))

    def test_invalid_rates_raise(self):
        with pytest.raises(ValueError):
            BernoulliBoolean(True, alpha=1.5)
        with pytest.raises(ValueError):
            BernoulliBoolean(True, beta=-0.1)


class TestErrorComposition:
    def test_and_reduces_fpr(self):
        # AND: both must be false positives
        a, b = compose_and(0.1, 0.0, 0.1, 0.0)
        assert a == pytest.approx(0.01)  # 0.1 * 0.1
        assert b == pytest.approx(0.0)

    def test_and_increases_fnr(self):
        # AND: either can be false negative
        a, b = compose_and(0.0, 0.1, 0.0, 0.1)
        assert a == pytest.approx(0.0)
        assert b == pytest.approx(0.19)  # 0.1 + 0.1 - 0.01

    def test_or_increases_fpr(self):
        # OR: either can be false positive
        a, b = compose_or(0.1, 0.0, 0.1, 0.0)
        assert a == pytest.approx(0.19)  # 0.1 + 0.1 - 0.01
        assert b == pytest.approx(0.0)

    def test_or_reduces_fnr(self):
        # OR: both must be false negatives
        a, b = compose_or(0.0, 0.1, 0.0, 0.1)
        assert a == pytest.approx(0.0)
        assert b == pytest.approx(0.01)  # 0.1 * 0.1

    def test_not_swaps_rates(self):
        a, b = compose_not(0.1, 0.2)
        assert a == 0.2
        assert b == 0.1


class TestTrapdoor:
    def test_create_trapdoor(self):
        factory = TrapdoorFactory(key=b'secret')
        t = factory.create("hello")
        assert len(t.hash) == 32

    def test_same_value_same_hash(self):
        factory = TrapdoorFactory(key=b'secret')
        t1 = factory.create("hello")
        t2 = factory.create("hello")
        assert t1 == t2

    def test_different_value_different_hash(self):
        factory = TrapdoorFactory(key=b'secret')
        t1 = factory.create("hello")
        t2 = factory.create("world")
        assert t1 != t2

    def test_different_key_different_hash(self):
        f1 = TrapdoorFactory(key=b'key1')
        f2 = TrapdoorFactory(key=b'key2')
        t1 = f1.create("hello")
        t2 = f2.create("hello")
        # Cannot directly compare, should raise
        with pytest.raises(ValueError):
            _ = t1 == t2

    def test_equals_returns_approximate(self):
        factory = TrapdoorFactory(key=b'secret')
        t1 = factory.create("hello")
        t2 = factory.create("hello")
        result = t1.equals(t2, fpr=0.001)
        assert isinstance(result, BernoulliBoolean)
        assert result.value is True
        assert result.alpha == 0.001


class TestBooleanSet:
    def test_create_from_values(self):
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b", "c"], factory)
        assert len(s) == 3

    def test_membership(self):
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b"], factory)
        t_a = factory.create("a")
        t_c = factory.create("c")
        assert t_a in s
        assert t_c not in s

    def test_contains_returns_approximate(self):
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b"], factory, alpha=0.1)
        t_a = factory.create("a")
        result = s.contains(t_a)
        assert result.value is True
        assert result.alpha == 0.1

    def test_union(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        union = s1 | s2
        assert len(union) == 3

    def test_intersection(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        intersection = s1 & s2
        assert len(intersection) == 1
        assert factory.create("b") in intersection

    def test_symmetric_difference(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        xor = s1 ^ s2
        assert len(xor) == 2  # a, c

    def test_difference(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        diff = s1 - s2
        assert len(diff) == 1
        assert factory.create("a") in diff

    def test_incompatible_keys_raise(self):
        f1 = TrapdoorFactory(key=b'key1')
        f2 = TrapdoorFactory(key=b'key2')
        s1 = BooleanSet.from_values(["a"], f1)
        s2 = BooleanSet.from_values(["b"], f2)
        with pytest.raises(ValueError):
            _ = s1 | s2

    def test_error_propagation_union(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a"], factory, alpha=0.1)
        s2 = BooleanSet.from_values(["b"], factory, alpha=0.1)
        union = s1 | s2
        # OR increases FPR
        assert union.alpha == pytest.approx(0.19)

    def test_error_propagation_intersection(self):
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory, alpha=0.1)
        s2 = BooleanSet.from_values(["b", "c"], factory, alpha=0.1)
        intersection = s1 & s2
        # AND decreases FPR
        assert intersection.alpha == pytest.approx(0.01)


class TestBernoulliTheory:
    """Tests for Bernoulli types theory features."""

    def test_confusion_matrix_structure(self):
        """Confusion matrix should be row-stochastic (rows sum to 1)."""
        av = BernoulliBoolean(True, alpha=0.1, beta=0.2)
        cm = av.confusion_matrix
        # Rows sum to 1 (row-stochastic)
        assert sum(cm[0]) == pytest.approx(1.0)
        assert sum(cm[1]) == pytest.approx(1.0)
        # Check values
        assert cm[0] == (pytest.approx(0.9), pytest.approx(0.1))  # [1-alpha, alpha]
        assert cm[1] == (pytest.approx(0.2), pytest.approx(0.8))  # [beta, 1-beta]

    def test_confusion_matrix_perfect(self):
        """Perfect observation has identity confusion matrix."""
        av = BernoulliBoolean(True, alpha=0.0, beta=0.0)
        cm = av.confusion_matrix
        assert cm == ((1.0, 0.0), (0.0, 1.0))

    def test_posterior_with_uniform_prior(self):
        """Posterior should increase when observed=True and beta=0."""
        av = BernoulliBoolean(True, alpha=0.1, beta=0.0)
        # With beta=0 and obs=True, posterior should increase from 0.5
        assert av.posterior(0.5) > 0.5

    def test_posterior_rare_event(self):
        """For rare events (low prior), false positives dominate."""
        # Classic medical test example: rare disease (1%), good test (1% FPR)
        av = BernoulliBoolean(True, alpha=0.01, beta=0.0)
        posterior = av.posterior(0.001)
        # Even with positive test, still unlikely to have disease
        assert posterior < 0.1

    def test_posterior_observed_false(self):
        """When observed=False, posterior should decrease."""
        av = BernoulliBoolean(False, alpha=0.0, beta=0.1)
        # With alpha=0 and obs=False, posterior should decrease from 0.5
        assert av.posterior(0.5) < 0.5

    def test_posterior_invalid_prior(self):
        """Prior must be in [0, 1]."""
        av = BernoulliBoolean(True, alpha=0.1, beta=0.1)
        with pytest.raises(ValueError):
            av.posterior(-0.1)
        with pytest.raises(ValueError):
            av.posterior(1.5)

    def test_mutual_information_perfect(self):
        """Perfect observation (alpha=beta=0) gives max info (1 bit)."""
        assert mutual_information(0.0, 0.0) == pytest.approx(1.0)

    def test_mutual_information_useless(self):
        """Useless observation (alpha=0.5, beta=0.5) gives no info."""
        assert mutual_information(0.5, 0.5) == pytest.approx(0.0)

    def test_mutual_information_bounds(self):
        """Mutual information should be in [0, 1] bits."""
        # Test various error rates
        for alpha in [0.0, 0.1, 0.3, 0.5]:
            for beta in [0.0, 0.1, 0.3, 0.5]:
                mi = mutual_information(alpha, beta)
                assert 0 <= mi <= 1

    def test_mutual_information_asymmetric(self):
        """MI depends on which type of error is present."""
        # FPR only vs FNR only should give same MI with uniform prior
        mi_fpr = mutual_information(0.2, 0.0, prior=0.5)
        mi_fnr = mutual_information(0.0, 0.2, prior=0.5)
        assert mi_fpr == pytest.approx(mi_fnr)

    def test_mutual_information_prior_effect(self):
        """Non-uniform priors affect mutual information."""
        mi_uniform = mutual_information(0.1, 0.1, prior=0.5)
        mi_skewed = mutual_information(0.1, 0.1, prior=0.1)
        # Different priors give different MI
        assert mi_uniform != pytest.approx(mi_skewed, rel=0.01)

    def test_mutual_information_invalid_params(self):
        """Invalid parameters should raise ValueError."""
        with pytest.raises(ValueError):
            mutual_information(-0.1, 0.0)
        with pytest.raises(ValueError):
            mutual_information(0.0, 1.5)
        with pytest.raises(ValueError):
            mutual_information(0.0, 0.0, prior=-0.1)

    def test_bernoulli_boolean_second_order(self):
        """BernoulliBoolean is second-order (allows alpha != beta)."""
        bb = BernoulliBoolean(True, alpha=0.1, beta=0.2)
        assert isinstance(bb, BernoulliBoolean)
        assert bb.value is True
        # Second-order: alpha != beta allowed
        assert bb.alpha == 0.1
        assert bb.beta == 0.2
        # First-order is a special case where alpha == beta
        first_order = BernoulliBoolean(True, alpha=0.1, beta=0.1)
        assert first_order.alpha == first_order.beta


class TestCardinalityTracking:
    """Tests for cardinality bound tracking in BooleanSet."""

    def test_initial_cardinality(self):
        """Sets track exact cardinality on creation."""
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b", "c"], factory)
        assert s.cardinality_bounds == (3, 3)

    def test_empty_set_cardinality(self):
        """Empty set has zero cardinality."""
        s = BooleanSet()
        assert s.cardinality_bounds == (0, 0)

    def test_add_increases_cardinality(self):
        """Adding element increases cardinality bounds."""
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a"], factory)
        assert s.cardinality_bounds == (1, 1)
        s.add(factory.create("b"))
        assert s.cardinality_bounds == (2, 2)

    def test_add_existing_no_change(self):
        """Adding existing element doesn't change cardinality."""
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b"], factory)
        assert s.cardinality_bounds == (2, 2)
        s.add(factory.create("a"))  # Already exists
        assert s.cardinality_bounds == (2, 2)

    def test_union_cardinality_bounds(self):
        """Union: max(k1,k2) <= |union| <= k1+k2."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        union = s1 | s2
        low, high = union.cardinality_bounds
        assert low == 2  # max(2, 2)
        assert high == 4  # 2 + 2
        assert low <= len(union) <= high

    def test_intersection_cardinality_bounds(self):
        """Intersection: 0 <= |intersection| <= min(k1,k2)."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b", "c"], factory)
        s2 = BooleanSet.from_values(["b", "c", "d"], factory)
        intersection = s1 & s2
        low, high = intersection.cardinality_bounds
        assert low == 0
        assert high == 3  # min(3, 3)
        assert low <= len(intersection) <= high

    def test_xor_cardinality_bounds(self):
        """XOR: |k1-k2| <= |xor| <= k1+k2."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b", "c"], factory)
        s2 = BooleanSet.from_values(["b", "c"], factory)
        xor = s1 ^ s2
        low, high = xor.cardinality_bounds
        # low = |3-2| = 1, high = 3+2 = 5
        assert low <= len(xor)
        assert len(xor) <= high

    def test_difference_cardinality_bounds(self):
        """Difference: max(0, k1-k2) <= |diff| <= k1."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b", "c"], factory)
        s2 = BooleanSet.from_values(["b"], factory)
        diff = s1 - s2
        low, high = diff.cardinality_bounds
        assert low == max(0, 3 - 1)  # 2
        assert high == 3
        assert low <= len(diff) <= high


class TestSizeDependentFPR:
    """Tests for size-dependent FPR calculation."""

    def test_membership_fpr_empty_set(self):
        """Empty set has zero FPR."""
        s = BooleanSet()
        assert s.membership_fpr() == 0.0

    def test_membership_fpr_single_element(self):
        """Single element FPR matches formula."""
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a"], factory)
        # k=1: (1 - 2^{-2})^256 = (1 - 0.25)^256
        expected = (1 - 2**(-2))**256
        assert s.membership_fpr(n_bits=256) == pytest.approx(expected)

    def test_membership_fpr_increases_with_size(self):
        """FPR should increase as set size increases."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a"], factory)
        s2 = BooleanSet.from_values(["a", "b", "c", "d"], factory)

        fpr1 = s1.membership_fpr(n_bits=64)
        fpr2 = s2.membership_fpr(n_bits=64)
        # Larger set has higher FPR
        assert fpr2 > fpr1

    def test_membership_fpr_decreases_with_bits(self):
        """FPR should decrease as hash size increases."""
        factory = TrapdoorFactory()
        s = BooleanSet.from_values(["a", "b", "c"], factory)

        fpr_small = s.membership_fpr(n_bits=64)
        fpr_large = s.membership_fpr(n_bits=256)
        # More bits = lower FPR
        assert fpr_large < fpr_small

    def test_subset_fpr_formula(self):
        """Subset FPR matches theoretical formula."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)  # k1=2
        s2 = BooleanSet.from_values(["x", "y", "z"], factory)  # k2=3

        # (1 - (1 - 2^{-k1}) * 2^{-k2})^n
        k1, k2, n = 2, 3, 128
        expected = (1 - (1 - 2**(-k1)) * 2**(-k2))**n
        assert s1.subset_fpr(s2, n_bits=n) == pytest.approx(expected)

    def test_subset_fpr_empty_set(self):
        """Empty sets have zero subset FPR."""
        factory = TrapdoorFactory()
        s1 = BooleanSet()
        s2 = BooleanSet.from_values(["a"], factory)
        # Note: empty set needs same key fingerprint
        s1._key_fingerprint = factory.key_fingerprint
        assert s1.subset_fpr(s2) == 0.0

    def test_fpr_through_operations(self):
        """FPR should be computable after set operations."""
        factory = TrapdoorFactory()
        s1 = BooleanSet.from_values(["a", "b"], factory)
        s2 = BooleanSet.from_values(["c", "d", "e"], factory)
        union = s1 | s2

        # After union, should be able to compute FPR
        fpr = union.membership_fpr(n_bits=128)
        assert 0 < fpr < 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
