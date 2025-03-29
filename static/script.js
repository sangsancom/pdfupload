document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("uploadForm");
    const fileInput = document.getElementById("pdfFile");
    const downloadSection = document.getElementById("downloadSection");
    const downloadLink = document.getElementById("downloadLink");

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // 폼 제출 기본 동작 막기

        const file = fileInput.files[0];
        if (!file) {
            alert("PDF 파일을 선택해주세요.");
            return;
        }

        const formData = new FormData();
        formData.append("pdfFile", file);

        // 서버에 POST 요청
        fetch("/convert", {
            method: "POST",
            body: formData,
        })
        .then((res) => {
            if (!res.ok) {
                throw new Error("변환 실패");
            }
            return res.blob(); // 변환된 PNG를 Blob으로 받음
        })
        .then((blob) => {
            const url = window.URL.createObjectURL(blob);
            downloadLink.href = url;
            downloadLink.download = "converted.png"; // 다운로드 파일명
            downloadSection.style.display = "block"; // 다운로드 링크 표시
        })
        .catch((err) => {
            console.error("에러:", err);
            alert("파일 변환 중 오류가 발생했습니다.");
        });
    });
});
