"""The five guidance arms: their system prompts and their user turns, pinned byte for byte.

The pinned values were computed from the request the app sends, so a change to the surgery, the
prompt files or the turn builder shows up here.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from gloss_eval import paths, runner
from gloss_eval.guidance import (
    ANCHOR,
    ARMS,
    EXAMPLE,
    RULE,
    SECOND_EXAMPLE,
    PromptDrift,
    build,
    build_all,
)
from gloss_eval.request import haber_clause, system_prompt

PROMPT_SHA256 = {
    "no-guidance": "9ebc8be922604db32bb850521240bdffc79d6cbade09ec2c6fdd648ffe78e040",
    "rule": "3a6bc0581c3c8be2fda90b396624882c4e1b41ff51d052a4c7e956d290d17261",
    "rule+example": "8afa46d34bb411ee71ffc0bdf8595e106730286acf341ebb84bf67d6893e5010",
    "second-example": "9dca326f3ea5243d5aa2f4020dbc76847e3c7310302d0f1e039d76bdf3829ad3",
    "turn-clause": "8afa46d34bb411ee71ffc0bdf8595e106730286acf341ebb84bf67d6893e5010",
}

#: sha256 of the user turn each arm sends for each case in cases/haber.json.
TURN_SHA256 = {
    ("haberlo-sabido", "no-guidance"):
        "2079dea998ee227dceeb86398b65e194600c9836785161c21d19b0f62119b99c",
    ("haberlo-sabido", "rule"):
        "2079dea998ee227dceeb86398b65e194600c9836785161c21d19b0f62119b99c",
    ("haberlo-sabido", "rule+example"):
        "2079dea998ee227dceeb86398b65e194600c9836785161c21d19b0f62119b99c",
    ("haberlo-sabido", "second-example"):
        "2079dea998ee227dceeb86398b65e194600c9836785161c21d19b0f62119b99c",
    ("haberlo-sabido", "turn-clause"):
        "5cdd4152bc4005a89634fe3bbfdc2a7c08b42c183ec7a57212f35e8bb7499961",
    ("haberle-desobedecido", "no-guidance"):
        "67e068a09d13b43ede656cc252f5fee6ef511889177bd240c8929e04916dbdc1",
    ("haberle-desobedecido", "rule"):
        "67e068a09d13b43ede656cc252f5fee6ef511889177bd240c8929e04916dbdc1",
    ("haberle-desobedecido", "rule+example"):
        "67e068a09d13b43ede656cc252f5fee6ef511889177bd240c8929e04916dbdc1",
    ("haberle-desobedecido", "second-example"):
        "67e068a09d13b43ede656cc252f5fee6ef511889177bd240c8929e04916dbdc1",
    ("haberle-desobedecido", "turn-clause"):
        "ecee0fe6864d4db2f93ebf5913c8f41fcbb758d19f7aa59c7b7486324845532f",
    ("haberlos-dejado", "no-guidance"):
        "76d6ae831ff09722e10bda352b9efdf4495b08c6e0545b34f8e81b1caa46d01c",
    ("haberlos-dejado", "rule"):
        "76d6ae831ff09722e10bda352b9efdf4495b08c6e0545b34f8e81b1caa46d01c",
    ("haberlos-dejado", "rule+example"):
        "76d6ae831ff09722e10bda352b9efdf4495b08c6e0545b34f8e81b1caa46d01c",
    ("haberlos-dejado", "second-example"):
        "76d6ae831ff09722e10bda352b9efdf4495b08c6e0545b34f8e81b1caa46d01c",
    ("haberlos-dejado", "turn-clause"):
        "9936bc8bbe7289b1ef243677124b467a50709c02ac79ca6442c882f8db039d30",
    ("haberse-lavado", "no-guidance"):
        "0dab804853b0fbb357738c830fba0879189f9b3e7216b1040c18be833fb9d2f3",
    ("haberse-lavado", "rule"):
        "0dab804853b0fbb357738c830fba0879189f9b3e7216b1040c18be833fb9d2f3",
    ("haberse-lavado", "rule+example"):
        "0dab804853b0fbb357738c830fba0879189f9b3e7216b1040c18be833fb9d2f3",
    ("haberse-lavado", "second-example"):
        "0dab804853b0fbb357738c830fba0879189f9b3e7216b1040c18be833fb9d2f3",
    ("haberse-lavado", "turn-clause"):
        "2421d3e862903498e7b1cdf9e6b64a7431999013cf44ac833a20cfc757f9caf3",
    ("haberme-robado", "no-guidance"):
        "82494f276e1c249e3f93a1ce51c89c66dbbd442f3fe7e16090a6c721961b7050",
    ("haberme-robado", "rule"):
        "82494f276e1c249e3f93a1ce51c89c66dbbd442f3fe7e16090a6c721961b7050",
    ("haberme-robado", "rule+example"):
        "82494f276e1c249e3f93a1ce51c89c66dbbd442f3fe7e16090a6c721961b7050",
    ("haberme-robado", "second-example"):
        "82494f276e1c249e3f93a1ce51c89c66dbbd442f3fe7e16090a6c721961b7050",
    ("haberme-robado", "turn-clause"):
        "21b7475d8c9f9a14c2bf424e1b29928669332d37f40c11af07ddeb0180c2c68a",
    ("haberme-quejado", "no-guidance"):
        "9667cb33eef8579998a7b21b97870b5c8b0d07dd4f42e7b0d6cb45a9aabb2cec",
    ("haberme-quejado", "rule"):
        "9667cb33eef8579998a7b21b97870b5c8b0d07dd4f42e7b0d6cb45a9aabb2cec",
    ("haberme-quejado", "rule+example"):
        "9667cb33eef8579998a7b21b97870b5c8b0d07dd4f42e7b0d6cb45a9aabb2cec",
    ("haberme-quejado", "second-example"):
        "9667cb33eef8579998a7b21b97870b5c8b0d07dd4f42e7b0d6cb45a9aabb2cec",
    ("haberme-quejado", "turn-clause"):
        "d7544e93311aca976d84e5df55cf652b0a146b5b9f66cc517a37d29885202b61",
    ("haberte-oido", "no-guidance"):
        "cada308ab72613d60490f2c36b7e13d889b6f4eca1e9705a9632465bc73a92c6",
    ("haberte-oido", "rule"):
        "cada308ab72613d60490f2c36b7e13d889b6f4eca1e9705a9632465bc73a92c6",
    ("haberte-oido", "rule+example"):
        "cada308ab72613d60490f2c36b7e13d889b6f4eca1e9705a9632465bc73a92c6",
    ("haberte-oido", "second-example"):
        "cada308ab72613d60490f2c36b7e13d889b6f4eca1e9705a9632465bc73a92c6",
    ("haberte-oido", "turn-clause"):
        "3376267af93c1892350deb631496a3d294915a20c86122b0fd6d719127fd3f91",
    ("haberte-ocultado", "no-guidance"):
        "47555e2af07118ea403234a30e78b827acd9ea9705994f0158d0f7447171ce9a",
    ("haberte-ocultado", "rule"):
        "47555e2af07118ea403234a30e78b827acd9ea9705994f0158d0f7447171ce9a",
    ("haberte-ocultado", "rule+example"):
        "47555e2af07118ea403234a30e78b827acd9ea9705994f0158d0f7447171ce9a",
    ("haberte-ocultado", "second-example"):
        "47555e2af07118ea403234a30e78b827acd9ea9705994f0158d0f7447171ce9a",
    ("haberte-ocultado", "turn-clause"):
        "e70cc5b715d5d57e0c3ceb4fe3c834b09fbf86ed43df9455eaa2373ab4d15c04",
    ("haberle-cogido", "no-guidance"):
        "8f299f3bdef4717f0035e22027fcdc0fec799133ec3de7da15156246a90d49f4",
    ("haberle-cogido", "rule"):
        "8f299f3bdef4717f0035e22027fcdc0fec799133ec3de7da15156246a90d49f4",
    ("haberle-cogido", "rule+example"):
        "8f299f3bdef4717f0035e22027fcdc0fec799133ec3de7da15156246a90d49f4",
    ("haberle-cogido", "second-example"):
        "8f299f3bdef4717f0035e22027fcdc0fec799133ec3de7da15156246a90d49f4",
    ("haberle-cogido", "turn-clause"):
        "e34c25c1e259dc3bcd4cc68f9fd8ef3d6dac2f465ecaa984524e601bb3647f35",
    ("haberle-librado", "no-guidance"):
        "a4d0f14306eba5958cfb9a53a2f08407439ff49305664d469072b23f5d930ac2",
    ("haberle-librado", "rule"):
        "a4d0f14306eba5958cfb9a53a2f08407439ff49305664d469072b23f5d930ac2",
    ("haberle-librado", "rule+example"):
        "a4d0f14306eba5958cfb9a53a2f08407439ff49305664d469072b23f5d930ac2",
    ("haberle-librado", "second-example"):
        "a4d0f14306eba5958cfb9a53a2f08407439ff49305664d469072b23f5d930ac2",
    ("haberle-librado", "turn-clause"):
        "f941c351c3e08182ce7766cc58937e182976c6245ad729e2f877df125998f6c0",
    ("haberse-repuesto", "no-guidance"):
        "9e0683736679f961f7ab11bde950396ff46a1312d0760a7a682376bbe1c69c38",
    ("haberse-repuesto", "rule"):
        "9e0683736679f961f7ab11bde950396ff46a1312d0760a7a682376bbe1c69c38",
    ("haberse-repuesto", "rule+example"):
        "9e0683736679f961f7ab11bde950396ff46a1312d0760a7a682376bbe1c69c38",
    ("haberse-repuesto", "second-example"):
        "9e0683736679f961f7ab11bde950396ff46a1312d0760a7a682376bbe1c69c38",
    ("haberse-repuesto", "turn-clause"):
        "59999d839fffcba865f0af39d901908e63e535c7ae6d50520c70ff7ba321603e",
    ("haberse-formado", "no-guidance"):
        "fc2b354d7949486281644280a112254a0c8f8b5988bff6ebeb40fccd2aa0c554",
    ("haberse-formado", "rule"):
        "fc2b354d7949486281644280a112254a0c8f8b5988bff6ebeb40fccd2aa0c554",
    ("haberse-formado", "rule+example"):
        "fc2b354d7949486281644280a112254a0c8f8b5988bff6ebeb40fccd2aa0c554",
    ("haberse-formado", "second-example"):
        "fc2b354d7949486281644280a112254a0c8f8b5988bff6ebeb40fccd2aa0c554",
    ("haberse-formado", "turn-clause"):
        "de53bad214528329b3cb55101a48a9a229d6084652ba4ad71529caf5c34e7e58",
    ("habiendole-herido", "no-guidance"):
        "d7a1ea9a47a30e2b43d46c4b58f448ffb9e444c9e7ef6ea663db3f77104eec58",
    ("habiendole-herido", "rule"):
        "d7a1ea9a47a30e2b43d46c4b58f448ffb9e444c9e7ef6ea663db3f77104eec58",
    ("habiendole-herido", "rule+example"):
        "d7a1ea9a47a30e2b43d46c4b58f448ffb9e444c9e7ef6ea663db3f77104eec58",
    ("habiendole-herido", "second-example"):
        "d7a1ea9a47a30e2b43d46c4b58f448ffb9e444c9e7ef6ea663db3f77104eec58",
    ("habiendole-herido", "turn-clause"):
        "6d7588b2a6e546e3551c1ff2c819f3c22901b7a5e701b97efd5b331e8ade1d08",
    ("habiendolo-tocado", "no-guidance"):
        "d103aba2e539aa71146bc431050d70e7761b28ae41b41dc343611ad1d9837ce8",
    ("habiendolo-tocado", "rule"):
        "d103aba2e539aa71146bc431050d70e7761b28ae41b41dc343611ad1d9837ce8",
    ("habiendolo-tocado", "rule+example"):
        "d103aba2e539aa71146bc431050d70e7761b28ae41b41dc343611ad1d9837ce8",
    ("habiendolo-tocado", "second-example"):
        "d103aba2e539aa71146bc431050d70e7761b28ae41b41dc343611ad1d9837ce8",
    ("habiendolo-tocado", "turn-clause"):
        "8fcd661dbd0d314557011de87d1f9b7c3f241284ace3c7558fecd39ede36539b",
    ("habiendoles-dado", "no-guidance"):
        "825f3ef6fce45975a4a8769efebee25ed1c300bd84dafc018f0d41edff621fd6",
    ("habiendoles-dado", "rule"):
        "825f3ef6fce45975a4a8769efebee25ed1c300bd84dafc018f0d41edff621fd6",
    ("habiendoles-dado", "rule+example"):
        "825f3ef6fce45975a4a8769efebee25ed1c300bd84dafc018f0d41edff621fd6",
    ("habiendoles-dado", "second-example"):
        "825f3ef6fce45975a4a8769efebee25ed1c300bd84dafc018f0d41edff621fd6",
    ("habiendoles-dado", "turn-clause"):
        "f3dc707d625cb80000b01a3900dd08172c5e5016cb3206c436a2ab8b6ae44ef6",
    ("habiendose-puesto", "no-guidance"):
        "a95fc53f94bfed869a31df9142c2fad0aca230912bc3d7ac1eaebfab3a232e1d",
    ("habiendose-puesto", "rule"):
        "a95fc53f94bfed869a31df9142c2fad0aca230912bc3d7ac1eaebfab3a232e1d",
    ("habiendose-puesto", "rule+example"):
        "a95fc53f94bfed869a31df9142c2fad0aca230912bc3d7ac1eaebfab3a232e1d",
    ("habiendose-puesto", "second-example"):
        "a95fc53f94bfed869a31df9142c2fad0aca230912bc3d7ac1eaebfab3a232e1d",
    ("habiendose-puesto", "turn-clause"):
        "0af4cd20d07ec40feb6511430d83d4329ab5d33f13756ea1450573b6733db6b8",
}

FULL_TURNS = {
    ("haberlo-sabido", "no-guidance"): (
        "Translate this Spanish text into English: “haberlo”\n"
        "It appears in this sentence: “—Nadie podía «haberlo» sabido.”\n"
        "Earlier in the passage, for sense only. It cannot change the marked words — passage “Quintana”, marked text “Quintanar”, answer “Quintanar”. The passage: “Era un sobre común, de color agrisado. La dirección: “Sir Enrique Baskerville, Northumberland Hotel” , estaba escrita con letra muy tosca; el sello postal decía: “Charing Cross” y tenía la fecha y la hora de la noche anterior. ¿Quién sabía que usted iba a alojarse en el Northumberland Hotel? — preguntó Holmes, clavando los ojos en sir Enrique Baskerville.”"
    ),
    ("haberlo-sabido", "turn-clause"): (
        "Translate this Spanish text into English: “haberlo”\n"
        "This word is the auxiliary \"haber\" with a pronoun attached. The participle that follows it in the sentence is outside the selection and must not appear in the translation. Translate the auxiliary and its pronoun only, with an ellipsis where the participle would sit: \"haberle\" before \"dicho\" is \"having … him\", never \"having told him\" or \"having … told him\".\n"
        "It appears in this sentence: “—Nadie podía «haberlo» sabido.”\n"
        "Earlier in the passage, for sense only. It cannot change the marked words — passage “Quintana”, marked text “Quintanar”, answer “Quintanar”. The passage: “Era un sobre común, de color agrisado. La dirección: “Sir Enrique Baskerville, Northumberland Hotel” , estaba escrita con letra muy tosca; el sello postal decía: “Charing Cross” y tenía la fecha y la hora de la noche anterior. ¿Quién sabía que usted iba a alojarse en el Northumberland Hotel? — preguntó Holmes, clavando los ojos en sir Enrique Baskerville.”"
    ),
    ("habiendose-puesto", "second-example"): (
        "Translate this Spanish text into English: “Habiéndose”\n"
        "It appears in this sentence: “«Habiéndose» puesto en camino juntos encontraron un hormiguero.”\n"
        "Earlier in the passage, for sense only. It cannot change the marked words — passage “Quintana”, marked text “Quintanar”, answer “Quintanar”. The passage: “Fue a buscarlos su hermano menor, al que llamaban el Simple, pero cuando los encontró comenzaron a burlarse de él, porque en su sencillez pretendía saber dirigirse en un mundo donde se habían perdido ellos dos, ellos dos que tenían mucho más talento que él.”"
    ),
}

HABER_CASES = json.loads((paths.CASES_DIR / "haber.json").read_text(encoding="utf-8"))


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_the_arms_come_in_ladder_order():
    assert ARMS == ("no-guidance", "rule", "rule+example", "second-example", "turn-clause")


def test_system_prompts_are_pinned():
    assert {arm: _sha(p) for arm, p in build_all(system_prompt()).items()} == PROMPT_SHA256


def test_rule_plus_example_and_turn_clause_are_the_prompt_file():
    assert build("rule+example", system_prompt()) == system_prompt()
    assert build("turn-clause", system_prompt()) == system_prompt()


def test_no_guidance_is_the_prompt_without_both_sentences():
    shipped = system_prompt()
    built = build("no-guidance", shipped)
    assert RULE not in built and EXAMPLE not in built
    assert built == shipped.replace(f" {RULE} {EXAMPLE}", "")


def test_reinserting_both_sentences_reproduces_the_prompt():
    built = build("no-guidance", system_prompt())
    assert built.replace(ANCHOR, f"{ANCHOR} {RULE} {EXAMPLE}", 1) == system_prompt()


def test_rule_keeps_the_rule_and_drops_the_example():
    built = build("rule", system_prompt())
    assert RULE in built and EXAMPLE not in built
    assert built == system_prompt().replace(f" {EXAMPLE}", "")


def test_second_example_follows_the_first():
    built = build("second-example", system_prompt())
    assert built == system_prompt().replace(EXAMPLE, f"{EXAMPLE} {SECOND_EXAMPLE}")


@pytest.mark.parametrize("edit", [
    lambda p: p.replace("verb it anticipates", "verb it expects"),
    lambda p: p.replace(EXAMPLE, "So «haberla» is \"having … it\"."),
    lambda p: p.replace(ANCHOR, "Never absorb meaning from outside the span."),
    lambda p: p.replace(f" {RULE} {EXAMPLE}", f" {EXAMPLE} {RULE}"),
    lambda p: p.replace(EXAMPLE, f"{EXAMPLE} {SECOND_EXAMPLE}"),
])
def test_a_drifted_prompt_fails_to_build(edit):
    drifted = edit(system_prompt())
    assert drifted != system_prompt()
    for arm in ARMS:
        with pytest.raises(PromptDrift, match="drifted"):
            build(arm, drifted)


def test_unknown_arm_is_refused():
    with pytest.raises(ValueError):
        build("rule+two-examples", system_prompt())


def test_every_user_turn_is_pinned():
    built = {(case["id"], arm): _sha(runner.arm_turn("guidance", arm, case))
             for case in HABER_CASES for arm in ARMS}
    assert built == TURN_SHA256


@pytest.mark.parametrize("key", list(FULL_TURNS))
def test_selected_user_turns_in_full(key):
    case_id, arm = key
    case = next(c for c in HABER_CASES if c["id"] == case_id)
    assert runner.arm_turn("guidance", arm, case) == "".join(FULL_TURNS[key])


def test_only_turn_clause_carries_the_haber_clause():
    for case in HABER_CASES:
        for arm in ARMS:
            turn = runner.arm_turn("guidance", arm, case)
            assert (haber_clause() in turn) == (arm == "turn-clause")
            assert "«" in turn and "Earlier in the passage" in turn
