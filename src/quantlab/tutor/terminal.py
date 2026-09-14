"""Optional Phase 4 interface; all questions and grading stay in the tutor service."""


def checkpoint(tutor, contexts, *, read, write):
    if not tutor.progress.data["settings"]["enabled"]:
        return
    view = tutor.study(contexts)
    question = view["current"]["question"]
    write("QUANT TUTOR: " + question["quantlab"])
    write(question["prompt"])
    for option in question["options"]:
        write(option["id"] + ": " + option["text"])
    while not view["current"]["closed"]:
        answer = read(
            "Tutor answer (choice ID; blank skips; multiple reasons comma-separated): "
        ).strip()
        if not answer:
            write("Tutor skipped. No answer credit; trading continues.")
            return
        if question["answer_type"] == "choices":
            answer = [value.strip() for value in answer.split(",")]
        try:
            view = tutor.answer(view["current"]["id"], answer)
        except ValueError as exc:
            write(str(exc))
            continue
        write(view["current"]["feedback"])
    for name, explanation in view["current"]["question"].get("layers", {}).items():
        write(name.upper() + ": " + explanation)
