def score_questions(
    questions,
    answers,
):
    score = 0

    for i, question in enumerate(
        questions
    ):

        user_answer = str(
            answers.get(
                str(i),
                "",
            )
        ).strip().lower()

        correct_answer = (
            str(
                question.answer
            )
            .strip()
            .lower()
        )

        # --------------------------------------------
        # No answer
        # --------------------------------------------

        if not user_answer:
            continue

        # --------------------------------------------
        # MCQ / True False
        # --------------------------------------------

        if question.type in {
            "MCQ",
            "True / False",
        }:

            if user_answer == correct_answer:
                score += 1

            continue

        # --------------------------------------------
        # Short Answer
        # --------------------------------------------

        if question.type == "Short Answer":

            keywords = [
                str(k).strip().lower()
                for k in question.keywords
                if str(k).strip()
            ]

            if keywords:

                matched = sum(
                    1
                    for keyword in keywords
                    if keyword in user_answer
                )

                if matched >= 1:
                    score += 1

            else:

                answer_words = [
                    word
                    for word in correct_answer.split()
                    if len(word) > 3
                ]

                if answer_words:

                    matched = sum(
                        1
                        for word in answer_words
                        if word in user_answer
                    )

                    if (
                        matched
                        >= max(
                            1,
                            len(answer_words) // 3,
                        )
                    ):
                        score += 1

                elif (
                    user_answer
                    == correct_answer
                ):
                    score += 1

    return score
