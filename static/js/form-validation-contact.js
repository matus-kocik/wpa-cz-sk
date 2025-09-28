
const firstNameInput = document.querySelector("#id_first_name");
const firstNameError = document.querySelector("#first-name-error");
const lastNameInput = document.querySelector("#id_last_name");
const lastNameError = document.querySelector("#last-name-error");
const emailInput = document.querySelector("#id_email");
const emailError = document.querySelector("#email-error");
const subjectInput = document.querySelector("#id_subject");
const subjectError = document.querySelector("#subject-error");
const messageBodyInput = document.querySelector("#id_message_body");
const messageBodyError = document.querySelector("#message_body-error");
const containsHtmlTags = (text) => /<[^>]+>/.test(text);


const nameRegex = /^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽáéíóúýďťňřščžäëïöüÄËÏÖÜ' -]+$/;
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

function handleNameValidation(input, errorElem, fieldLabel) {
    input.addEventListener("input", () => {
        const value = input.value.trim();

        if (value === "") {
            errorElem.textContent = "";
            return;
        }

        if (value.length < 2) {
            errorElem.textContent = `${fieldLabel} musí mít alespoň 2 znaky.`;
        } else if (!nameRegex.test(value)) {
            errorElem.textContent = `${fieldLabel} může obsahovat pouze písmena, mezery, pomlčky nebo apostrof.`;
        } else {
            errorElem.textContent = "";
        }
    });

input.addEventListener("blur", () => {
    if (input.value.trim() === "") {
    errorElem.textContent = "";
    }
});
}

handleNameValidation(firstNameInput, firstNameError, "Jméno");
handleNameValidation(lastNameInput, lastNameError, "Příjmení");

// Email validation
emailInput.addEventListener("input", () => {
const value = emailInput.value.trim();

if (value === "") {
    emailError.textContent = "";
return;
}

if (!emailRegex.test(value)) {
    emailError.textContent = "Zadejte platnou e-mailovou adresu.";
} else {
    emailError.textContent = "";
}
});

emailInput.addEventListener("blur", () => {
if (emailInput.value.trim() === "") {
    emailError.textContent = "";
}
});

// Subject validation
subjectInput.addEventListener("input", () => {
const value = subjectInput.value.trim();

if (value === "") {
    subjectError.textContent = "";
return;
}

if (value.length < 3) {
    subjectError.textContent = "Předmět musí mít alespoň 3 znaky.";
} else if (!/[a-zA-Zá-žÁ-Ž]/.test(value)) {
    subjectError.textContent = "Předmět musí obsahovat alespoň jedno písmeno.";
} else if (containsHtmlTags(value)) {
    subjectError.textContent = "Předmět nesmí obsahovat HTML značky.";
} else {
    subjectError.textContent = "";
}
});

subjectInput.addEventListener("blur", () => {
if (subjectInput.value.trim() === "") {
    subjectError.textContent = "";
}
});

// Message body validation
messageBodyInput.addEventListener("input", () => {
const value = messageBodyInput.value.trim();

if (value === "") {
    messageBodyError.textContent = "";
return;
}

if (value.length < 10) {
    messageBodyError.textContent = "Zpráva musí mít alespoň 10 znaků.";
} else if (!/[a-zA-Zá-žÁ-Ž]/.test(value)) {
    messageBodyError.textContent = "Zpráva musí obsahovat text.";
} else if (containsHtmlTags(value)) {
    messageBodyError.textContent = "Zpráva nesmí obsahovat HTML značky.";
} else {
    messageBodyError.textContent = "";
}
});

messageBodyInput.addEventListener("blur", () => {
if (messageBodyInput.value.trim() === "") {
    messageBodyError.textContent = "";
}
});
