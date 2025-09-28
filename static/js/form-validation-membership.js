const firstNameInput = document.querySelector("#id_first_name");
const firstNameError = document.querySelector("#first-name-error");
const lastNameInput = document.querySelector("#id_last_name");
const lastNameError = document.querySelector("#last-name-error");
const emailInput = document.querySelector("#id_email");
const emailError = document.querySelector("#email-error");
const academicTitleInput = document.querySelector("#id_academic_title");
const academicTitleError = document.querySelector("#academic-title-error");
const birthDateInput = document.querySelector("#id_birth_date");
const birthDateError = document.querySelector("#birth-date-error");
const phoneNumberInput = document.querySelector("#id_phone_number");
const phoneNumberError = document.querySelector("#phone-number-error");
const streetInput = document.querySelector("#id_street");
const streetError = document.querySelector("#street-error");
const houseNumberInput = document.querySelector("#id_house_number");
const houseNumberError = document.querySelector("#house-number-error");
const cityInput = document.querySelector("#id_city");
const cityError = document.querySelector("#city-error");
const districtInput = document.querySelector("#id_district");
const districtError = document.querySelector("#district-error");
const postalCodeInput = document.querySelector("#id_postal_code");
const postalCodeError = document.querySelector("#postal-code-error");
const notesInput = document.querySelector("#id_notes");
const notesError = document.querySelector("#notes-error");
const containsHtmlTags = (text) => /<[^>]+>/.test(text);
const declarationPlaceInput = document.querySelector("#id_declaration_place");
const declarationPlaceError = document.querySelector("#declaration-place-error");
const declarationSignatureInput = document.querySelector("#id_declaration_signature");
const declarationSignatureError = document.querySelector("#declaration-signature-error");


const nameRegex = /^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽáéíóúýďťňřščžäëïöüÄËÏÖÜ' -]+$/;
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const academicTitleRegex = /^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽáéíóúýďťňřščž. ]+$/;
const phoneNumberRegex = /^\+\d{8,15}$/;
const streetRegex = /^[A-Za-zÁÉÍÓÚÝČĎĚŇŘŠŤŽáéíóúýčďěňřšťž0-9\s.\-\/]+$/;
const houseNumberRegex = /^[0-9A-Za-zÁÉÍÓÚÝČĎĚŇŘŠŤŽáéíóúýčďěňřšťž\s\/\-]+$/;
const locationRegex = /^[A-Za-zÁÉÍÓÚÝĎŤŇŘŠČŽäëïöüÄËÏÖÜáéíóúýďťňřščž0-9.,()'\- ]+$/;
const postalCodeRegex = /^[\w\s\-]{3,10}$/;


// Name validation
const handleNameValidation = (input, errorElem, fieldLabel) => {
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
};

handleNameValidation(firstNameInput, firstNameError, "Jméno");
handleNameValidation(lastNameInput, lastNameError, "Příjmení");

// Email validation
emailInput.addEventListener("input", () => {
const value = emailInput.value.trim();

if (value === "") {
    emailError.textContent = "";
return;
}

emailError.textContent = emailRegex.test(value)
? ""
: "Zadejte platnou e-mailovou adresu.";
});

emailInput.addEventListener("blur", () => {
if (emailInput.value.trim() === "") {
    emailError.textContent = "";
}
});

// Academic title validation
academicTitleInput.addEventListener("input", () => {
const value = academicTitleInput.value.trim();

if (value === "") {
    academicTitleError.textContent = "";
return;
}

academicTitleError.textContent = academicTitleRegex.test(value)
? ""
: "Titul může obsahovat pouze písmena, mezery a tečky.";
});

academicTitleInput.addEventListener("blur", () => {
if (academicTitleInput.value.trim() === "") {
    academicTitleError.textContent = "";
}
});

// Birth date validation
const isOver18 = (dateStr) => {
const today = new Date();
const birthDate = new Date(dateStr);
const age = today.getFullYear() - birthDate.getFullYear();
const m = today.getMonth() - birthDate.getMonth();
return age > 18 || (age === 18 && (m > 0 || (m === 0 && today.getDate() >= birthDate.getDate())));
};

const isInFuture = (dateStr) => {
const birthDate = new Date(dateStr);
const today = new Date();
return birthDate > today;
};

const isTooOld = (dateStr) => {
const birthDate = new Date(dateStr);
return birthDate.getFullYear() < 1900;
};

birthDateInput.addEventListener("input", () => {
const value = birthDateInput.value.trim();

if (value === "") {
    birthDateError.textContent = "";
return;
}

if (isTooOld(value)) {
    birthDateError.textContent = "Datum narození musí být po roce 1900.";
} else if (isInFuture(value)) {
    birthDateError.textContent = "Datum narození nemůže být v budoucnosti.";
} else if (!isOver18(value)) {
    birthDateError.textContent = "Musíte být starší 18 let.";
} else {
    birthDateError.textContent = "";
}
});

birthDateInput.addEventListener("blur", () => {
if (birthDateInput.value.trim() === "") {
    birthDateError.textContent = "";
}
});

// Phone number validation
phoneNumberInput.addEventListener("input", () => {
const value = phoneNumberInput.value.trim();

if (value === "") {
    phoneNumberError.textContent = "";
return;
}

if (!phoneNumberRegex.test(value)) {
    phoneNumberError.textContent = "Zadejte telefonní číslo v mezinárodním formátu, např. +420123456789.";
} else {
    phoneNumberError.textContent = "";
}
});

phoneNumberInput.addEventListener("blur", () => {
if (phoneNumberInput.value.trim() === "") {
    phoneNumberError.textContent = "";
}
});

// Street validation
streetInput.addEventListener("input", () => {
const value = streetInput.value.trim();

if (value === "") {
    streetError.textContent = "";
return;
}

if (!streetRegex.test(value)) {
    streetError.textContent = "Ulice může obsahovat pouze písmena, čísla, mezery, pomlčky, tečky a lomítka.";
} else {
    streetError.textContent = "";
}
});

streetInput.addEventListener("blur", () => {
if (streetInput.value.trim() === "") {
    streetError.textContent = "";
}
});

// House number validation
houseNumberInput.addEventListener("input", () => {
const value = houseNumberInput.value.trim();

if (value === "") {
    houseNumberError.textContent = "";
return;
}

if (!houseNumberRegex.test(value)) {
    houseNumberError.textContent = "Číslo domu může obsahovat pouze čísla, písmena, mezery, lomítka a pomlčky.";
} else {
    houseNumberError.textContent = "";
}
});

houseNumberInput.addEventListener("blur", () => {
if (houseNumberInput.value.trim() === "") {
    houseNumberError.textContent = "";
}
});

// City validation
cityInput.addEventListener("input", () => {
const value = cityInput.value.trim();
if (value === "") {
    cityError.textContent = "";
return;
}

if (!locationRegex.test(value)) {
    cityError.textContent = "Použijte platný název města – povolena písmena, čísla, tečky, čárky, pomlčky.";
} else {
    cityError.textContent = "";
}
});

cityInput.addEventListener("blur", () => {
if (cityInput.value.trim() === "") {
    cityError.textContent = "";
}
});

// District validation
districtInput.addEventListener("input", () => {
const value = districtInput.value.trim();

if (value === "") {
    districtError.textContent = "";
return;
}

if (!locationRegex.test(value)) {
    districtError.textContent = "Použijte platný název okresu – povolena písmena, čísla, pomlčky, tečky.";
} else {
    districtError.textContent = "";
}
});

districtInput.addEventListener("blur", () => {
if (districtInput.value.trim() === "") {
    districtError.textContent = "";
}
});

// Postal code validation
postalCodeInput.addEventListener("input", () => {
const value = postalCodeInput.value.trim();

if (value === "") {
    postalCodeError.textContent = "";
return;
}

postalCodeError.textContent = postalCodeRegex.test(value)
? ""
: "Zadejte platné PSČ – čísla, písmena, mezery, pomlčky.";
});

postalCodeInput.addEventListener("blur", () => {
if (postalCodeInput.value.trim() === "") {
    postalCodeError.textContent = "";
}
});

// Notes validation
notesInput.addEventListener("input", () => {
const value = notesInput.value.trim();
if (value.length > 256) {
    notesError.textContent = "Poznámka může mít maximálně 256 znaků.";
} else if (containsHtmlTags(value)) {
    notesError.textContent = "Poznámka nesmí obsahovat HTML značky.";
} else {
    notesError.textContent = "";
}
});

notesInput.addEventListener("blur", () => {
if (notesInput.value.trim() === "") {
    notesError.textContent = "";
}
});

// Declaration place
declarationPlaceInput.addEventListener("input", () => {
const value = declarationPlaceInput.value.trim();
if (value === "") {
    declarationPlaceError.textContent = "";
return;
}
if (!locationRegex.test(value)) {
    declarationPlaceError.textContent = "Zadejte platný název místa – pouze písmena, čísla, mezery.";
} else {
    declarationPlaceError.textContent = "";
}
});

// Declaration signature
declarationSignatureInput.addEventListener("input", () => {
const value = declarationSignatureInput.value.trim();
if (value === "") {
    declarationSignatureError.textContent = "";
return;
}
if (!nameRegex.test(value)) {
    declarationSignatureError.textContent = "Podpis může obsahovat pouze jméno – písmena, mezery, pomlčky.";
} else {
    declarationSignatureError.textContent = "";
}
});
