// ===============================
// 답변 등록
// ===============================

const answerSubmitButton = document.querySelector("#answer-submit");
const answerContent = document.querySelector("#answer-content");
const answerMessage = document.querySelector("#answer-message");


answerSubmitButton.addEventListener("click", () => {

    const content = answerContent.value.trim();

    if (content === "") {
        answerMessage.textContent = "답변을 입력해주세요.";
        return;
    }

    answerMessage.textContent = "답변이 입력되었습니다.";

    console.log("작성한 답변:", content);
});


// ===============================
// 별점
// ===============================

const ratings = document.querySelectorAll(".rating");


ratings.forEach((rating) => {

    const stars = rating.querySelectorAll(".star");
    const result = rating.querySelector(".rating-result");


    stars.forEach((star) => {

        star.addEventListener("click", () => {

            const score = Number(star.dataset.score);

            const answerId = rating.dataset.answerId;


            // 별 활성화
            stars.forEach((item) => {

                const itemScore = Number(item.dataset.score);

                if (itemScore <= score) {
                    item.classList.add("active");
                } else {
                    item.classList.remove("active");
                }

            });


            // 선택 결과 출력
            result.textContent = `${score}점으로 평가했습니다.`;


            // 현재는 확인용
            console.log("답변 ID:", answerId);
            console.log("평점:", score);

        });

    });

});