const PHONE_REGEX = /^[\+]?[0-9]*/;

const RUNNING_SINCE = 2021;

let TODAY = new Date(new Date().setHours(0, 0, 0, 0));

const CURRENT_MONTH = TODAY.getMonth();

const CURRENT_YEAR = TODAY.getFullYear();

const CURRENT_DAY = TODAY.getDate();

const CURRENT_WEEKDAY = TODAY.getDay();

Date.locale = {
  en: {
    monthNames: [
      "January",
      "February",
      "March",
      "April",
      "May",
      "June",
      "July",
      "August",
      "September",
      "October",
      "November",
      "December",
    ],
    dayNames: [
      "Monday",
      "Tuesday",
      "Wednesday",
      "Thursday",
      "Friday",
      "Saturday",
      "Sunday",
    ],
  },
  es: {
    monthNames: [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ],
    dayNames: [
      "Lunes",
      "Martes",
      "Miercoles",
      "Jueves",
      "Viernes",
      "Sabado",
      "Domingo",
    ],
  },
};

Date.prototype.getMonthName = (number, lang = "en") => {
  return Date.locale[lang].monthNames[number];
};

Date.prototype.getMonthNumber = (name, lang = "en") => {
  return Date.locale[lang].monthNames.indexOf(name);
};

Date.prototype.getMonthDays = (monthNumber) => {
  let d = new Date(CURRENT_YEAR, monthNumber + 1, 0);
  return d.getDate();
};

Date.prototype.getDaysList = (monthNumber) => {
  let dayCount = Date.prototype.getMonthDays(monthNumber);
  return Array.from({ length: dayCount }, (_, i) => i + 1);
};

Date.prototype.getDayName = (date, lang = "en") => {
  return date.toLocaleString(lang, { weekday: "short" });
};

const YEARS = Array.from(Array(CURRENT_YEAR + 5 - RUNNING_SINCE), (_, i) => ({
  value: i + RUNNING_SINCE,
  label: i + RUNNING_SINCE,
  selected: i + RUNNING_SINCE === CURRENT_YEAR,
}));

const MONTHS = Array.from(Array(12).keys()).map((v) => ({
  value: v,
  label: Date.prototype.getMonthName(v),
  selected: v === CURRENT_MONTH,
}));

const nameCell = (name, photoUrl) => `
    <td class="px-6 py-4 whitespace-nowrap">
      <div class="flex items-center">
        <div class="flex-shrink-0 h-10 w-10">
          <img
            class="h-10 w-10 rounded-full"
            src=${photoUrl.startsWith("/") ? photoUrl : "/" + photoUrl}
          />
        </div>
        <div class="ml-4">
          <div class="text-sm font-medium text-gray-900">
            ${name}
          </div>
        </div>
      </div>
    </td>
    `;

const generateActiveCell = (userId, value, fn) => `
      <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm text-gray-900 text-center">
          ${
            fn
              ? `
            <button onclick="${fn}(${userId})" class="focus:outline-none">
              <span id="active-${userId}" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  value ? "bg-green-100" : "bg-red-100"
                } text-green-800">
                ${value ? "Active" : "Inactive"}
              </span> 
            </button>`
              : `
            <span id="active-${userId}" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  value ? "bg-green-100" : "bg-red-100"
                } text-green-800">
              ${value ? "Active" : "Inactive"}
            </span> 
            `
          }
        </div>
      </td>`;

const generateActionsCell = (id, fnSuffix, _delete=true, _edit=true) => `
    <td>
      <div class="flex space-x-2 justify-center">
        ${_delete ? `<button onclick="delete${fnSuffix}Confirm(${id})" class="rounded-full hover:bg-gray-300 px-2 py-2">
        <img src="/static/icons/delete.svg" width="16"/>
      </button>`: ''}
        ${_edit ? `<button onclick="update${fnSuffix}(${id})" class="rounded-full hover:bg-gray-300 px-2 py-2">
        <img src="/static/icons/edit.svg" width="16"/>
      </button>` : ''}
      </div>
    </td
`;

const generateSelectDoctorCell = (id, fn) => `
    <td>
      <div class="flex justify-center">
        <button class="rounded-full hover:bg-gray-300 px-2 py-2" onclick="${fn}(${id})">
          <img id='icon-${id}' src="/static/icons/swap.svg" width="16"/>
        </button>
      </div>
    </td
`;

const generateColumn = (colName) => `
      <th scope="col" id="${colName}" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
        ${colName}
      </th>`;

const generateCell = (value) => `
      <td class="px-6 py-4 whitespace-nowrap">
        <div class="text-sm text-gray-900 text-center">
            ${value}
        </div>
      </td>`; //generic cell generator

const generateRow = (cells, rowId) => `
    <tr id="row-${rowId}">
        ${cells.join("\n")}
    </tr>
    `;

const generateTable = (tableId, colNames, rows) => `
    <div class="border-b border-gray-200 sm:rounded-lg overflow-y-auto h-full">
        <table class="divide-y divide-gray-200 w-full h-full" id="${tableId}">
            <thead class="bg-gray-50">
                <tr>
                    ${colNames.map((name) => generateColumn(name)).join("\n")}
                </tr>
            </thead>
            <tbody>
                ${rows.join("\n")}
            </tbody>
        </table>
    </div>
    `;

const generatePhoneChip = (value) => `
    <div id='${value}' class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 bg-turqoise h-8">
        <span class="px-1 w-full leading-none text-white text-center text-white font-bold">
            ${value}
        </span>
        <button onclick="deletePhone(${value})" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
            <img src="/static/icons/delete.svg" width="16" height="16" />
        </button>
    </div>
    `;

const generateSpecialtiesField = (chips) => `
<div class="flex h-full">
  <span class="text-sm border bg-blue-50 font-bold uppercase border-2 rounded-l px-4 py-2 bg-gray-50 whitespace-no-wrap w-2/6">
    Specialties
  </span>
  <div class="shadow-sm flex flex-wrap items-center justify-center md:justify-start px-4 gap-1 w-4/6">
    <div class="flex flex-row w-full" id="container-Specialties">
      ${chips}
    </div>
    <div class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 h-8">
      <div>
        <input id='new-Specialties' type="text" class="px-1 w-full text-black text-center focus:outline-none" value=""/> 
      </div>
      <button onclick="addSpecialty()" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
        <img src="/static/icons/add.svg" width="16" height="16" class="-mx-1"/>
      </button>
    </div>  
  </div>
</div>
    `;

const generateSpecialtyChip = (value) => `
    <div id='${value}' class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 bg-turqoise h-8">
      <span class="px-1 w-full leading-none text-white text-center text-white font-bold">
          ${value}
      </span>
      <button onclick="deleteSpecialty('${value}')" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
          <img src="/static/icons/delete.svg" width="16" height="16" />
      </button>
    </div>
    `;

const generateRoleChip = (value, roleColor) => `
    <div id="${value}" class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 ${roleColor} h-8">
      <span class="px-1 w-full leading-none text-white text-center font-bold">
        ${value}
      </span>
      <button onclick="toggleRole('${value}')" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
            <img id="icon-${value}" src="/static/icons/add.svg" width="16" height="16" />
      </button>
    </div>
        `;

const generateDayChip = (value) => `
    <div class="inline-flex items-center rounded-full px-1 py-2 h-8">
      <button id="${value}" onclick="selectDay(${value})" class="h-6 w-8 rounded-full focus:outline-none hover:bg-turqoise hover:text-white text-gray-500">
        <span class="px-1 w-full leading-none text-center">
          ${value}
        </span>
      </button>
    </div>
`;

const generateDropDown = (id, options) => `
    <div class="relative inline-flex">
        <svg class="w-2 h-2 absolute top-0 right-0 m-4 pointer-events-none" xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 412 232">
            <path d="M206 171.144L42.678 7.822c-9.763-9.763-25.592-9.763-35.355 0-9.763 9.764-9.763 25.592 0 35.355l181 181c4.88 4.882 11.279 7.323 17.677 7.323s12.796-2.441 17.678-7.322l181-181c9.763-9.764 9.763-25.592 0-35.355-9.763-9.763-25.592-9.763-35.355 0L206 171.144z" fill="#648299" fill-rule="nonzero" />
        </svg>
        <select id='${id}' class="border border-gray-300 rounded-lg text-gray-600 h-10 pl-5 pr-10 bg-white hover:border-gray-400 focus:outline-none appearance-none">
          ${options.map((op) =>
            op.selected
              ? `<option value=${
                  op.value !== undefined ? op.value : op
                } selected>${op.label ? op.label : op}</option>`
              : `<option value=${op.value !== undefined ? op.value : op}>${
                  op.label ? op.label : op
                }</option>`
          )}
        </select>
    </div>
`;

const generateSymptomChip = (value) => `
    <div id='${value}' class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 bg-turqoise h-8">
        <span class="px-1 w-full leading-none text-white text-center text-white font-bold">
            ${value}
        </span>
        <button onclick="deleteSymptom(${value})" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
            <img src="/static/icons/delete.svg" width="16" height="16" />
        </button>
    </div>
    `;

const generateCsChip = (value) => `
    <div id='${value}' class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 bg-turqoise h-8">
        <span class="px-1 w-full leading-none text-white text-center text-white font-bold">
            ${value}
        </span>
        <button onclick="deleteClinicalSign(${value})" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
            <img src="/static/icons/delete.svg" width="16" height="16" />
        </button>
    </div>
    `;
  
const generateDiseaseChip = (value) => `
    <div id='${value}' class="inline-flex items-center rounded-full border border-gray-200 px-1 py-2 bg-turqoise h-8">
        <span class="px-1 w-full leading-none text-white text-center text-white font-bold">
            ${value}
        </span>
        <button onclick="deleteDisease(${value})" class="h-5 w-5 rounded-full bg-opacity-25 focus:outline-none">
            <img src="/static/icons/delete.svg" width="16" height="16" />
        </button>
    </div>
    `;

const generateConfirmationModal = (id, fn, title='Confirm action', body='Changes will remain permanent, proceed?') => `
<div id="modal-${id}" class="fixed z-50 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
  <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>
    <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
    <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
      <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
        <div class="sm:flex sm:items-start">
          <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
            <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
            <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
              ${title}
            </h3>
            <div class="mt-2">
              <p class="text-sm text-gray-500">
                ${body}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
        <button onclick="${fn}(${id}, 'confirm')" type="button" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm">
          Confirm
        </button>
        <button onclick="${fn}(${id}, 'cancel')" type="button" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
          Cancel
        </button>
      </div>
    </div>
  </div>
</div>
`

const setPagination = async (
  tablename,
  offset,
  limit,
  paginationContainer,
  fn,
  conditions = null,
  operator=null
) => {
  let options = {};

  options.headers = {
    Accept: "application/json",
  };

  if (conditions) {
    try {
      options.body = JSON.stringify(conditions);
      options.method = "POST";
      options.headers["Content-Type"] = "application/json";
    } catch (e) {
      options.method = "GET";
    }
  }

  res = await fetch(`/api/pagination/total/${tablename}` + (operator ? `/${operator}` : ''), options);

  data = await res.json();

  if (res.status === 200) {
    let total = data.result;
    if (total < 1) {
      paginationContainer.innerHTML = "";
      return 0;
    }

    if (total < limit) {
      limit = total;
    }

    let itemsPerPage = limit - offset;

    if (itemsPerPage === 0){
      itemsPerPage = limit;
    }  

    let pageCount = total / itemsPerPage;

    let btns = Array(Math.ceil(pageCount)); //round up

    for (let i = 0; i < pageCount; i++) {
      btns.push(`
              <button class="rounded-xl bg-turqoise text-white font-bold px-2 text-center" onclick='${fn}(${
        itemsPerPage * i
      } ${options.body ? ", " + options.body : null})'>
              ${i + 1}
              </button>
            `);
    }
    paginationContainer.innerHTML = btns.join(" ");
    return total;
  } else {
    Promise.reject(data);
  }
};

const setPaginationFromTotal = (
  offset,
  limit,
  total,
  paginationContainer,
  fn
) => {
  if (total < 1) {
    paginationContainer.innerHTML = "";
    return 0;
  }

  if (total < limit) {
    limit = total;
  }
  let itemsPerPage = limit - offset;
  
  if (itemsPerPage === 0){
    itemsPerPage = limit;
  }

  let pageCount = total / itemsPerPage;

  let btns = Array(Math.ceil(pageCount)); //round up

  for (let i = 0; i < pageCount; i++) {
    btns.push(`
            <button class="rounded-xl bg-turqoise text-white font-bold px-2 text-center" onclick='${fn}(${
      itemsPerPage * i
    })'>
            ${i + 1}
            </button>
          `);
  }

  paginationContainer.innerHTML = btns.join("\n");
  return total;
};

const toggleLoadingModal = (forceHide = false, forceShow = false) => {
  const loadingModal = document.getElementById("loading-modal");
  if (forceHide) {
    loadingModal.classList.add("hidden");
  } else if (forceShow) {
    loadingModal.classList.remove("hidden");
  } else {
    loadingModal.classList.toggle("hidden");
  }
};

const delay = (time) => {
  return new Promise((resolve) => setTimeout(resolve, time));
};

const showOkModal = async (
  title = "Operation Successful",
  body = "You may keep operating now"
) => {
  toggleLoadingModal(true);
  const okModal = document.getElementById("ok-modal");

  document.getElementById("ok-modal-title").textContent = title;
  document.getElementById("ok-modal-body").textContent = body;
  okModal.classList.remove("hidden");

  delay(500).then(() => {
    window.location.href = window.location.href; //force reload on page
  });
};
