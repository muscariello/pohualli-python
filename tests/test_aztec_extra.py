from pohualli.aztec import aztec_tzolkin_name_to_number, number_to_aztec_tzolkin_name, aztec_haab_name_to_number, number_to_aztec_haab_name


def test_aztec_name_normalization_and_lookup():
    for i in range(20):
        name = number_to_aztec_tzolkin_name(i)
        idx = aztec_tzolkin_name_to_number(name.lower())
        assert idx == i
    for i in range(19):
        name = number_to_aztec_haab_name(i)
        idx = aztec_haab_name_to_number(name.lower())
        assert idx == i
    # unknown returns 255
    assert aztec_tzolkin_name_to_number('unknown') == 255
