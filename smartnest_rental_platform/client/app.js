const API_BASE = "http://127.0.0.1:5000/api";

async function fetchOptions() {
  const response = await fetch(`${API_BASE}/options`);
  if (!response.ok) {
    throw new Error("Failed to load options");
  }
  return response.json();
}

function populateSelect(select, options, placeholder) {
  select.innerHTML = "";
  const option = document.createElement("option");
  option.textContent = placeholder;
  option.value = "";
  option.disabled = true;
  option.selected = true;
  select.appendChild(option);

  options.forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item;
    opt.textContent = item;
    select.appendChild(opt);
  });
}

function buildPayload(prefix) {
  return {
    rent: document.getElementById(`${prefix}-rent`)?.value || 0,
    size: document.getElementById(`${prefix}-size`)?.value || 0,
    bhk: document.getElementById(`${prefix}-bhk`)?.value || 0,
    bathroom: document.getElementById(`${prefix}-bath`)?.value || 0,
    city: document.getElementById(`${prefix}-city`)?.value || "",
    area_type: document.getElementById(`${prefix}-area`)?.value || "",
    furnishing_status: document.getElementById(`${prefix}-furnish`)?.value || "",
    tenant_preferred: document.getElementById(`${prefix}-tenant`)?.value || "",
  };
}

function fieldName(id) {
  const map = {
    rent: "Rent",
    size: "Size",
    bhk: "BHK",
    bath: "Bathroom",
    city: "City",
    area: "Area Type",
    furnish: "Furnishing Status",
    tenant: "Tenant Preferred",
    'text-input': 'Text',
  };
  return map[id] || id;
}

function validateFields(prefix, required) {
  const missing = [];
  required.forEach((field) => {
    const el = document.getElementById(`${prefix}-${field}`) || document.getElementById(field);
    if (!el) return;
    const val = (el.value || "").toString().trim();
    const isNumberField = el.type === "number";
    if (isNumberField) {
      if (val === "" || Number(val) === 0) {
        missing.push(field);
      }
    } else {
      if (!val) missing.push(field);
    }
  });
  return missing;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Request failed");
  }
  return response.json();
}

async function init() {
  try {
    const options = await fetchOptions();
    document.querySelectorAll("select[data-options]").forEach((select) => {
      const key = select.dataset.options;
      populateSelect(select, options[key] || [], `Select ${key.replace("_", " ")}`);
    });
  } catch (err) {
    console.error(err);
  }

  document.getElementById("rent-btn").addEventListener("click", async () => {
    const output = document.getElementById("rent-output");
    const required = ["size", "bhk", "bath", "city", "area", "furnish", "tenant"];
    const missing = validateFields("rent", required);
    if (missing.length) {
      output.textContent = `Missing fields: ${missing.map((m) => fieldName(m)).join(", ")}. Please fill these out.`;
      return;
    }
    const payload = buildPayload("rent");
    output.textContent = "Estimating rent...";
    try {
      const data = await postJson(`${API_BASE}/predict_rent`, payload);
      output.textContent = `Estimated rent: INR ${data.estimated_rent}`;
    } catch (err) {
      output.textContent = "Unable to estimate rent. Check server.";
    }
  });

  document.getElementById("scam-btn").addEventListener("click", async () => {
    const output = document.getElementById("scam-output");
    const required = ["rent", "size", "bhk", "bath", "city", "area", "furnish", "tenant"];
    const missing = validateFields("scam", required);
    if (missing.length) {
      output.textContent = `Missing fields: ${missing.map((m) => fieldName(m)).join(", ")}. Please fill these out.`;
      return;
    }
    const payload = buildPayload("scam");
    output.textContent = "Analyzing listing...";
    try {
      const data = await postJson(`${API_BASE}/predict_scam`, payload);
      output.textContent = `Scam risk: ${data.label} | RF=${data.random_forest_probability} LR=${data.logistic_probability}`;
    } catch (err) {
      output.textContent = "Unable to analyze listing. Check server.";
    }
  });

  document.getElementById("text-btn").addEventListener("click", async () => {
    const output = document.getElementById("text-output");
    const textEl = document.getElementById("text-input");
    if (!textEl.value.trim()) {
      output.textContent = "Missing fields: Text. Please paste the listing text to verify.";
      return;
    }
    const text = textEl.value;
    output.textContent = "Verifying text...";
    try {
      const data = await postJson(`${API_BASE}/verify_text`, { text });
      output.textContent = `Text risk: ${data.label} | Probability=${data.probability}`;
    } catch (err) {
      output.textContent = "Unable to verify text. Check server.";
    }
  });

  document.getElementById("reco-btn").addEventListener("click", async () => {
    const output = document.getElementById("reco-output");
    const required = ["rent", "size", "bhk", "bath", "city", "area", "furnish", "tenant"];
    const missing = validateFields("reco", required);
    if (missing.length) {
      output.textContent = `Missing fields: ${missing.map((m) => fieldName(m)).join(", ")}. Please fill these out.`;
      return;
    }
    const payload = buildPayload("reco");
    output.textContent = "Finding similar listings...";
    try {
      const data = await postJson(`${API_BASE}/recommend`, payload);
      const items = data.recommendations || [];
      if (!items.length) {
        output.textContent = "No recommendations returned.";
        return;
      }
      output.innerHTML = items
        .map(
          (item) =>
            `City: ${item.City} | Area: ${item["Area Locality"]} | Rent: ${item.Rent} | Size: ${item.Size}`
        )
        .join("<br>");
    } catch (err) {
      output.textContent = "Unable to fetch recommendations. Check server.";
    }
  });

  document.getElementById("locality-btn").addEventListener("click", async () => {
    const output = document.getElementById("locality-output");
    const cityEl = document.getElementById("locality-city");
    if (!cityEl.value) {
      output.textContent = "Missing fields: City. Please select a city.";
      return;
    }
    const city = cityEl.value;
    output.textContent = "Analyzing locality...";
    try {
      const data = await postJson(`${API_BASE}/locality_cluster`, { city });
      if (data.error) {
        output.textContent = data.error;
        return;
      }
      output.textContent = `Cluster ${data.cluster} | Avg rent: INR ${data.avg_rent} | Avg size: ${data.avg_size} | Similar cities: ${data.similar_cities.join(", ")}`;
    } catch (err) {
      output.textContent = "Unable to analyze locality. Check server.";
    }
  });
}

window.addEventListener("load", init);
