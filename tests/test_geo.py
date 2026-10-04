import pytest

from bok.geo import avkoda_polyline, avstand_m, baring, punkter_langs, vaderstreck

KM_NORRUT = [(59.0, 18.0), (59.0 + 1000 / 111194.93, 18.0)]


def test_avkoda_googles_exempel():
    assert avkoda_polyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@") == [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]


def test_trasig_polyline():
    with pytest.raises(ValueError):
        avkoda_polyline("_p~iF~ps|U_")


def test_avstand_och_baring():
    assert avstand_m((0.0, 0.0), (1.0, 0.0)) == pytest.approx(111194.9, rel=1e-4)
    assert baring((0.0, 0.0), (1.0, 0.0)) == pytest.approx(0.0, abs=0.01)
    assert baring((0.0, 0.0), (0.0, 1.0)) == pytest.approx(90.0, abs=0.01)
    assert baring((1.0, 0.0), (0.0, 0.0)) == pytest.approx(180.0, abs=0.01)
    assert baring((0.0, 1.0), (0.0, 0.0)) == pytest.approx(270.0, abs=0.01)


def test_punkter_var_150_meter_och_malet():
    punkter = punkter_langs(KM_NORRUT, 150, 20)
    assert [round(m) for _, m, _ in punkter] == [0, 150, 300, 450, 600, 750, 900, 1000]
    assert all(r == pytest.approx(0.0, abs=0.01) for _, _, r in punkter)
    assert punkter[0][0] == KM_NORRUT[0]
    assert punkter[-1][0][0] == pytest.approx(KM_NORRUT[-1][0])


def test_punkter_sprids_nar_de_blir_for_manga():
    assert [round(m) for _, m, _ in punkter_langs(KM_NORRUT, 150, 3)] == [0, 500, 1000]
    assert [round(m) for _, m, _ in punkter_langs(KM_NORRUT, 150, 1)] == [0]


def test_punkter_specialfall():
    assert punkter_langs([], 150, 8) == []
    assert punkter_langs([(59.0, 18.0)], 150, 8) == [((59.0, 18.0), 0.0, 0.0)]
    med_dubblett = [KM_NORRUT[0], KM_NORRUT[0], KM_NORRUT[1]]
    assert all(r == pytest.approx(0.0, abs=0.01) for _, _, r in punkter_langs(med_dubblett, 500, 8))


@pytest.mark.parametrize("grader,namn", [(0, "norr"), (44, "nordost"), (90, "öst"), (180, "söder"),
                                         (270, "väst"), (338, "norr"), (315, "nordväst"), (360, "norr")])
def test_vaderstreck(grader, namn):
    assert vaderstreck(grader) == namn
