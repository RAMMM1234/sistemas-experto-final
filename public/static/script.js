const formulario = document.getElementById("formulario");
const modal = document.getElementById("modalHistorial");
const btnAbrir = document.getElementById("btnAbrirHistorial");
const btnCerrar = document.querySelector(".close-button");

if (formulario) {
    formulario.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const datos = Object.fromEntries(formData.entries());
        const resDiv = document.getElementById("resultado");

        resDiv.innerHTML = `<div class="resultado-card loading">Procesando diagnóstico...</div>`;
        resDiv.classList.remove("hidden");

        try {
            const respuesta = await fetch("/diagnostico", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datos),
            });

            const data = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(data.error || "No se pudo generar el diagnóstico.");
            }

            const colores = {
                danger: "#e74c3c",
                warning: "#f39c12",
                success: "#27ae60",
            };

            const color = colores[data.clase_css] || "#34495e";
            const avisoBD = data.guardado
                ? `<div class="db-ok">✓ Resultado guardado en PostgreSQL.</div>`
                : `<div class="db-warning">⚠ ${data.mensaje_db || "No se pudo guardar en PostgreSQL."}</div>`;

            resDiv.innerHTML = `
                <div class="resultado-animado" style="background:${color};">
                    <h3>${data.nivel}</h3>
                    <p>${data.mensaje}</p>
                    <div class="resultado-puntos">Puntaje de riesgo: ${data.puntos} puntos</div>
                    ${avisoBD}
                </div>
            `;

            resDiv.scrollIntoView({ behavior: "smooth" });
        } catch (error) {
            resDiv.innerHTML = `
                <div class="resultado-card error">
                    <h3>Error</h3>
                    <p>${error.message}</p>
                </div>
            `;
        }
    });
}

if (btnAbrir && modal) {
    btnAbrir.onclick = () => {
        modal.style.display = "block";
        cargarHistorial();
    };
}

if (btnCerrar && modal) {
    btnCerrar.onclick = () => (modal.style.display = "none");
}

window.onclick = (event) => {
    if (event.target === modal) modal.style.display = "none";
};

async function cargarHistorial() {
    const lista = document.getElementById("listaHistorial");
    if (!lista) return;

    lista.innerHTML = "<p class='historial-vacio'>Cargando historial...</p>";

    try {
        const respuesta = await fetch("/historial");
        const data = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(data.error || "No se pudo cargar el historial.");
        }

        lista.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            lista.innerHTML = "<p class='historial-vacio'>No hay registros aún.</p>";
            return;
        }

        data.forEach((item) => {
            const li = document.createElement("li");
            const fecha = item.fecha ? new Date(item.fecha).toLocaleString() : "Sin fecha";

            li.innerHTML = `
                <div class="historial-item">
                    <strong>${item.resultado}</strong><br>
                    <span>🔍 Síntomas: ${item.sintomas}</span><br>
                    <span>📊 Puntaje: ${item.puntos} puntos</span><br>
                    <small>📅 Fecha: ${fecha}</small>
                </div>
            `;
            lista.appendChild(li);
        });
    } catch (error) {
        lista.innerHTML = `<p class='historial-error'>${error.message}</p>`;
    }
}
