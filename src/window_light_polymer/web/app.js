const SVG_NS = "http://www.w3.org/2000/svg";

const modes = {
  thermoplastic: {
    family: "Thermoplastic polyurethane",
    summary: "Mostly linear segmented chains, held together in places by reversible hard-domain associations.",
    architecture: "Segmented chains",
    junction: "Physical domains",
    heatResponse: "Mobility rises",
    reshaping: "Often possible",
    note: "Dashed lines mark reversible associations—not new covalent bonds between chains.",
    heatedNote: "Heat weakens physical associations and increases chain mobility. A real processing window is grade-specific.",
  },
  thermoset: {
    family: "Thermoset polyurethane",
    summary: "A three-dimensional network in which covalent junctions permanently connect the polymer chains.",
    architecture: "Crosslinked network",
    junction: "Covalent bonds",
    heatResponse: "Network remains",
    reshaping: "Not by melting",
    note: "Filled junctions mark covalent crosslinks created by multifunctional reactants.",
    heatedNote: "Heat can soften segments, but the covalent network does not melt apart; excessive heat causes degradation.",
  },
};

const segmentFamilies = {
  polyether: {
    label: "Polyether",
    motif: "—R—O—R—O—",
    copy: "Polyether soft segments place ether oxygens along a flexible backbone. They change segment behavior, but they do not by themselves decide whether the whole polyurethane is a thermoplastic or thermoset.",
  },
  polyester: {
    label: "Polyester",
    motif: "—R—C(=O)—O—R—",
    copy: "Polyester soft segments add ester groups to the flexible block. The segment chemistry changes intermolecular interactions and durability, while overall functionality still controls chain versus network topology.",
  },
  polycaprolactone: {
    label: "Polycaprolactone",
    motif: "—R—C(=O)—O—(CH₂)₅—",
    copy: "Polycaprolactone is a semicrystalline polyester soft segment. Its melting transition can produce a pronounced change in local free-volume behavior, so Polly keeps it separate from the broader polyester category.",
  },
  polycarbonate: {
    label: "Polycarbonate",
    motif: "—R—O—C(=O)—O—R—",
    copy: "Polycarbonate soft segments contain carbonate groups within the flexible block. This is a chemistry choice inside the architecture, not a synonym for thermoplastic or thermoset behavior.",
  },
};

const state = {
  mode: "thermoplastic",
  segment: "polyether",
  heated: false,
};

const canvas = document.querySelector("#polymer-canvas");
const modeButtons = [...document.querySelectorAll(".mode-button")];
const heatButton = document.querySelector("#heat-button");
const segmentSelect = document.querySelector("#soft-segment");
const temperatureSlider = document.querySelector("#temperature-slider");
const temperatureOutput = document.querySelector("#temperature-output");
const tgAnchor = document.querySelector("#tg-anchor");
const additiveSizeInput = document.querySelector("#additive-size");
const additiveSizeOutput = document.querySelector("#additive-size-output");
const openingNow = document.querySelector("#opening-now");
const sizeCrossing = document.querySelector("#size-crossing");
const openingBand = document.querySelector("#opening-band");
const openingCurve = document.querySelector("#opening-curve");
const tgLine = document.querySelector("#tg-line");
const additiveLine = document.querySelector("#additive-line");
const additiveLineLabel = document.querySelector("#additive-line-label");
const temperatureCursor = document.querySelector("#temperature-cursor");
const temperaturePoint = document.querySelector("#temperature-point");
const temperatureMinLabel = document.querySelector("#temperature-min-label");
const temperatureTgLabel = document.querySelector("#temperature-tg-label");
const temperatureMaxLabel = document.querySelector("#temperature-max-label");
const openingLabel = document.querySelector("#opening-label");
const mapStatusTitle = document.querySelector("#map-status-title");
const mapStatusCopy = document.querySelector("#map-status-copy");
const thermalBoundaryCopy = document.querySelector("#thermal-boundary-copy");
const diameterYLabel = document.querySelector("#diameter-y-label");
const thermalSvgDescription = document.querySelector("#thermal-svg-description");

let polyurethaneTgAnchor = null;
let defaultTgAnchor = null;
let defaultTemperatureRange = { minimum: 200, maximum: 520 };
let palsProxyArtifact = null;

function svg(tag, attributes = {}, text = "") {
  const node = document.createElementNS(SVG_NS, tag);
  Object.entries(attributes).forEach(([name, value]) => node.setAttribute(name, value));
  if (text) node.textContent = text;
  return node;
}

function addLabel(group, x, y, label, className = "diagram-label") {
  group.append(svg("text", { x, y, class: className, "text-anchor": "middle" }, label));
}

function drawSegmentedChain(group, y, shift, reversed = false) {
  const direction = reversed ? -1 : 1;
  const xShift = state.heated ? shift : 0;
  const wave = state.heated ? 18 : 8;
  const path = `M 58 ${y} C 150 ${y - wave}, 210 ${y + wave}, 300 ${y} S 470 ${y - wave}, 702 ${y}`;
  group.append(svg("path", { d: path, class: "chain-backbone", transform: `translate(${xShift} 0)` }));

  const softBlocks = [88, 320, 558];
  const hardBlocks = [232, 480];
  softBlocks.forEach((x) => {
    const width = 112;
    group.append(svg("rect", {
      x: x + xShift,
      y: y - 17,
      width,
      height: 34,
      rx: 17,
      class: "soft-block",
    }));
  });
  hardBlocks.forEach((x) => {
    const adjustedX = x + xShift + direction * (state.heated ? 5 : 0);
    group.append(svg("rect", {
      x: adjustedX,
      y: y - 20,
      width: 62,
      height: 40,
      rx: 5,
      class: "hard-block",
    }));
    [adjustedX - 10, adjustedX + 72].forEach((linkX) => {
      group.append(svg("circle", { cx: linkX, cy: y, r: 7, class: "urethane-node" }));
    });
  });
}

function drawThermoplastic() {
  const group = svg("g", { class: `polymer-diagram ${state.heated ? "is-heated" : ""}` });
  const rows = [108, 215, 322];
  const shifts = [-18, 24, -12];
  rows.forEach((y, index) => drawSegmentedChain(group, y, shifts[index], index % 2 === 1));

  [264, 512].forEach((x) => {
    [128, 235].forEach((y) => {
      const bond = svg("line", {
        x1: x,
        y1: y,
        x2: x,
        y2: y + 67,
        class: "physical-bond",
      });
      if (state.heated) bond.classList.add("is-weakened");
      group.append(bond);
    });
  });

  addLabel(group, 145, 65, `${segmentFamilies[state.segment].label} soft segment`, "diagram-label emphasis");
  addLabel(group, 510, 65, "Hard segment domain", "diagram-label emphasis");
  addLabel(group, 380, 400, state.heated ? "physical associations loosen • chains gain mobility" : "dashed lines = reversible physical associations");
  canvas.append(group);
}

function drawNetworkEdge(group, from, to, index) {
  const midpoint = {
    x: (from.x + to.x) / 2,
    y: (from.y + to.y) / 2,
  };
  group.append(svg("line", {
    x1: from.x,
    y1: from.y,
    x2: to.x,
    y2: to.y,
    class: "network-edge",
  }));
  group.append(svg("circle", {
    cx: midpoint.x,
    cy: midpoint.y,
    r: 7,
    class: "urethane-node",
  }));
  if (index % 2 === 0) {
    group.append(svg("rect", {
      x: midpoint.x - 30,
      y: midpoint.y - 12,
      width: 22,
      height: 24,
      rx: 4,
      class: "hard-block",
      transform: `rotate(${Math.atan2(to.y - from.y, to.x - from.x) * 180 / Math.PI} ${midpoint.x - 19} ${midpoint.y})`,
    }));
  }
}

function drawThermoset() {
  const group = svg("g", { class: `polymer-diagram network ${state.heated ? "is-heated" : ""}` });
  const nodes = [
    { x: 105, y: 105 },
    { x: 350, y: 82 },
    { x: 630, y: 120 },
    { x: 195, y: 245 },
    { x: 470, y: 228 },
    { x: 675, y: 325 },
    { x: 320, y: 350 },
    { x: 75, y: 340 },
  ];
  const edges = [
    [0, 1], [1, 2], [0, 3], [1, 3], [1, 4], [2, 4], [2, 5], [3, 4], [3, 6], [3, 7], [4, 5], [4, 6], [5, 6], [6, 7],
  ];
  edges.forEach(([left, right], index) => drawNetworkEdge(group, nodes[left], nodes[right], index));
  nodes.forEach((node) => {
    group.append(svg("circle", { cx: node.x, cy: node.y, r: 14, class: "crosslink-node" }));
    group.append(svg("circle", { cx: node.x, cy: node.y, r: 4, class: "crosslink-core" }));
  });

  addLabel(group, 138, 65, `${segmentFamilies[state.segment].label} network strand`, "diagram-label emphasis");
  addLabel(group, 555, 65, "Covalent junction", "diagram-label emphasis");
  addLabel(group, 380, 405, state.heated ? "segments move more • covalent network remains" : "filled nodes = permanent covalent crosslinks");
  canvas.append(group);
}

function updateCanvas() {
  [...canvas.children].forEach((child) => {
    if (!child.matches("title, desc")) child.remove();
  });
  const title = canvas.querySelector("title");
  const description = canvas.querySelector("desc");
  if (state.mode === "thermoplastic") {
    title.textContent = "Thermoplastic polyurethane structure";
    description.textContent = state.heated
      ? "Three segmented chains with weakened physical associations and increased mobility."
      : "Three segmented chains connected by reversible physical associations.";
    drawThermoplastic();
  } else {
    title.textContent = "Thermoset polyurethane structure";
    description.textContent = state.heated
      ? "A heated covalently crosslinked polyurethane network whose junctions remain connected."
      : "A three-dimensional polyurethane network with permanent covalent junctions.";
    drawThermoset();
  }
}

function updateCopy() {
  const mode = modes[state.mode];
  document.querySelector("#family-name").textContent = mode.family;
  document.querySelector("#family-summary").textContent = mode.summary;
  document.querySelector("#architecture").textContent = mode.architecture;
  document.querySelector("#junction").textContent = mode.junction;
  document.querySelector("#heat-response").textContent = state.heated
    ? (state.mode === "thermoplastic" ? "Associations weaken" : "Crosslinks persist")
    : mode.heatResponse;
  document.querySelector("#reshaping").textContent = mode.reshaping;
  document.querySelector("#structure-note").textContent = state.heated ? mode.heatedNote : mode.note;
  document.querySelector("#segment-copy").textContent = segmentFamilies[state.segment].copy;

  const legend = document.querySelector("#junction-legend");
  legend.innerHTML = state.mode === "thermoplastic"
    ? '<i class="swatch physical" aria-hidden="true"></i>Physical association'
    : '<i class="swatch covalent" aria-hidden="true"></i>Covalent crosslink';

  heatButton.textContent = state.heated ? "Cool sample" : "Apply heat";
  heatButton.setAttribute("aria-pressed", String(state.heated));
}

function render() {
  updateCanvas();
  updateCopy();
}

function metricK(value) {
  return `${Number(value).toFixed(1)} K`;
}

function genericScenarioOpening(temperature) {
  const delta = temperature - polyurethaneTgAnchor;
  const slopeAboveTg = state.mode === "thermoplastic" ? 0.012 : 0.006;
  return 5 + (delta < 0 ? 0.003 * delta : slopeAboveTg * delta);
}

function selectedProxyCurve() {
  if (!palsProxyArtifact) return null;
  return palsProxyArtifact.curves[`${state.mode}:${state.segment}`] || null;
}

function interpolateProxy(curve, temperature) {
  const points = curve.points;
  if (!points.length || temperature < points[0].temperature_k || temperature > points[points.length - 1].temperature_k) {
    return null;
  }
  if (temperature === points[0].temperature_k) return points[0];
  for (let index = 1; index < points.length; index += 1) {
    const right = points[index];
    const left = points[index - 1];
    if (temperature <= right.temperature_k) {
      const fraction = (temperature - left.temperature_k) / (right.temperature_k - left.temperature_k);
      const uncertainty = left.diameter_uncertainty_a === null || right.diameter_uncertainty_a === null
        ? null
        : left.diameter_uncertainty_a + fraction * (right.diameter_uncertainty_a - left.diameter_uncertainty_a);
      return {
        temperature_k: temperature,
        diameter_a: left.diameter_a + fraction * (right.diameter_a - left.diameter_a),
        diameter_uncertainty_a: uncertainty,
      };
    }
  }
  return points[points.length - 1];
}

function openingAt(temperature) {
  const curve = selectedProxyCurve();
  const proxy = curve ? interpolateProxy(curve, temperature) : null;
  if (proxy) {
    return {
      diameter: proxy.diameter_a,
      uncertainty: proxy.diameter_uncertainty_a,
      kind: "pals_proxy",
    };
  }
  return {
    diameter: genericScenarioOpening(temperature),
    uncertainty: 0.8,
    kind: "generic_scenario",
  };
}

function configureThermalRange() {
  const curve = selectedProxyCurve();
  if (curve) {
    temperatureSlider.min = String(Math.floor(curve.temperature_range_k[0]));
    temperatureSlider.max = String(Math.ceil(curve.temperature_range_k[1]));
    polyurethaneTgAnchor = curve.tg_k === null ? null : Number(curve.tg_k);
  } else {
    temperatureSlider.min = String(defaultTemperatureRange.minimum);
    temperatureSlider.max = String(defaultTemperatureRange.maximum);
    polyurethaneTgAnchor = defaultTgAnchor;
  }
  const minimum = Number(temperatureSlider.min);
  const maximum = Number(temperatureSlider.max);
  const current = Number(temperatureSlider.value);
  temperatureSlider.value = String(
    current < minimum || current > maximum || !Number.isFinite(current)
      ? Math.round((minimum + maximum) / 2)
      : current
  );
}

function chartPath(points) {
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(2)} ${point.y.toFixed(2)}`).join(" ");
}

function updateThermalProxy() {
  const temperature = Number(temperatureSlider.value);
  const additiveSize = Math.min(12, Math.max(2, Number(additiveSizeInput.value) || 5));
  const minimumTemperature = Number(temperatureSlider.min);
  const maximumTemperature = Number(temperatureSlider.max);
  const chart = { left: 78, right: 680, top: 40, bottom: 300, minimumOpening: 2, maximumOpening: 12 };
  const x = (value) => chart.left + (value - minimumTemperature) / (maximumTemperature - minimumTemperature) * (chart.right - chart.left);
  const y = (value) => chart.bottom - (value - chart.minimumOpening) / (chart.maximumOpening - chart.minimumOpening) * (chart.bottom - chart.top);
  const samples = Array.from({ length: 81 }, (_, index) => minimumTemperature + (maximumTemperature - minimumTemperature) * index / 80);
  const sampleOpenings = samples.map((value) => openingAt(value));
  const middle = samples.map((value, index) => ({ x: x(value), y: y(sampleOpenings[index].diameter) }));
  const hasCompleteUncertainty = sampleOpenings.every((opening) => opening.uncertainty !== null);
  const upper = samples.map((value, index) => ({ x: x(value), y: y(sampleOpenings[index].diameter + (sampleOpenings[index].uncertainty || 0)) }));
  const lower = [...samples].reverse().map((value, reverseIndex) => {
    const index = samples.length - 1 - reverseIndex;
    return { x: x(value), y: y(sampleOpenings[index].diameter - (sampleOpenings[index].uncertainty || 0)) };
  });
  const currentOpening = openingAt(temperature);
  let crossingTemperature = null;
  for (let index = 0; index < sampleOpenings.length; index += 1) {
    if (sampleOpenings[index].diameter >= additiveSize) {
      if (index === 0) {
        crossingTemperature = samples[0];
      } else {
        const previousOpening = sampleOpenings[index - 1].diameter;
        const denominator = sampleOpenings[index].diameter - previousOpening;
        const fraction = denominator === 0 ? 0 : (additiveSize - previousOpening) / denominator;
        crossingTemperature = samples[index - 1] + fraction * (samples[index] - samples[index - 1]);
      }
      break;
    }
  }
  const additiveY = y(additiveSize);
  const cursorX = x(temperature);
  const pointY = y(currentOpening.diameter);
  const curve = selectedProxyCurve();
  const isProxy = currentOpening.kind === "pals_proxy";

  temperatureOutput.textContent = metricK(temperature);
  additiveSizeOutput.textContent = `${additiveSize.toFixed(1)} Å`;
  openingNow.textContent = `${currentOpening.diameter.toFixed(2)} Å · ${isProxy ? "PALS proxy" : "scenario"}`;
  sizeCrossing.textContent = crossingTemperature === null
    ? `No crossing from ${Math.round(minimumTemperature)}–${Math.round(maximumTemperature)} K`
    : `≈ ${Math.round(crossingTemperature)} K · ${isProxy ? "local-cavity proxy" : "geometric scenario"}`;
  openingCurve.setAttribute("d", chartPath(middle));
  openingBand.setAttribute("d", hasCompleteUncertainty ? `${chartPath(upper)} ${chartPath(lower).replace(/^M/, "L")} Z` : "");
  if (polyurethaneTgAnchor === null) {
    tgLine.setAttribute("visibility", "hidden");
    temperatureTgLabel.textContent = "Tg not reported";
    temperatureTgLabel.setAttribute("x", String(x((minimumTemperature + maximumTemperature) / 2)));
    tgAnchor.textContent = "Not reported for this curve";
  } else {
    tgLine.setAttribute("visibility", "visible");
    tgLine.setAttribute("x1", String(x(polyurethaneTgAnchor)));
    tgLine.setAttribute("x2", String(x(polyurethaneTgAnchor)));
    temperatureTgLabel.setAttribute("x", String(x(polyurethaneTgAnchor)));
    temperatureTgLabel.textContent = `Tg ${Math.round(polyurethaneTgAnchor)} K`;
    tgAnchor.textContent = metricK(polyurethaneTgAnchor);
  }
  additiveLine.setAttribute("y1", String(additiveY));
  additiveLine.setAttribute("y2", String(additiveY));
  additiveLineLabel.setAttribute("y", String(Math.max(chart.top + 14, Math.min(chart.bottom - 6, additiveY - 8))));
  additiveLineLabel.textContent = `${additiveSize.toFixed(1)} Å additive`;
  temperatureCursor.setAttribute("x1", String(cursorX));
  temperatureCursor.setAttribute("x2", String(cursorX));
  temperaturePoint.setAttribute("cx", String(cursorX));
  temperaturePoint.setAttribute("cy", String(pointY));
  temperatureMinLabel.textContent = `${Math.round(minimumTemperature)} K`;
  temperatureMaxLabel.textContent = `${Math.round(maximumTemperature)} K`;
  openingLabel.textContent = isProxy ? "PALS proxy cavity diameter now" : "Scenario opening now";
  if (isProxy) {
    const evidence = palsProxyArtifact.data;
    const excluded = Number(curve.excluded_observations_from_live_interpolation || 0);
    const seriesCount = Array.isArray(curve.available_series) ? curve.available_series.length : 1;
    diameterYLabel.textContent = "PALS local cavity diameter proxy (Å)";
    thermalSvgDescription.textContent = "A literature PALS spherical-equivalent cavity-diameter proxy with an additive-size line and temperature cursor.";
    mapStatusTitle.textContent = "Literature PALS evidence is live";
    mapStatusCopy.textContent = `${curve.points.length} live observations · ${curve.label}. Evidence set: ${evidence.numeric_surrogate_points} numeric PALS points, ${evidence.independent_polymer_series} polymer series, ${evidence.independent_surrogate_sources} independent papers. ${seriesCount > 1 ? `${seriesCount} matched series are kept separate; Polly displays the most temperature-resolved one and uses recorded curation priority only to break ties. ` : ""}${excluded ? `${excluded} higher-temperature points are retained for audit but excluded from interpolation under the authors' reliability warning. ` : ""}Interpolation stops at the accepted source limits.`;
    thermalBoundaryCopy.textContent = "This curve is data-anchored to PALS local cavity diameters, not connected openings. A crossing does not establish diffusion, partitioning, migrated mass, leaching, or safety.";
  } else {
    diameterYLabel.textContent = "scenario accessible opening diameter (Å)";
    thermalSvgDescription.textContent = "A provisional polyurethane opening scenario with an additive-size line and temperature cursor.";
    mapStatusTitle.textContent = "No matched PALS curve yet";
    mapStatusCopy.textContent = "Polly is showing the original Tg-anchored scenario for this family and topology. It is not literature calibrated.";
    thermalBoundaryCopy.textContent = "Tg is data-anchored; the Å curve is a generic scenario for this selection. Replace it with matched PALS or MD evidence before treating the crossing as quantitative.";
  }
}

async function loadModelCard() {
  const response = await fetch("/api/model-card");
  if (!response.ok) throw new Error("Run window-light-polymer-train to generate the model card.");
  const card = await response.json();
  const polyurethane = card.evaluation.polyurethane_ood_test;
  const general = card.evaluation.general_polymer_audit;
  const puChange = Number(polyurethane.mae_change_k);
  const generalChange = Number(general.mae_change_k);

  document.querySelector("#pu-mae-base").textContent = metricK(polyurethane.base.mae_k);
  document.querySelector("#pu-mae-tuned").textContent = metricK(polyurethane.fine_tuned.mae_k);
  document.querySelector("#general-mae-delta").textContent = `${generalChange >= 0 ? "+" : ""}${generalChange.toFixed(1)} K`;
  document.querySelector("#pu-test-count").textContent = `${polyurethane.base.records} unusual polyurethane records`;
  document.querySelector("#dataset-count").textContent = `${card.dataset.polyurethane_records} polyurethane records`;
  document.querySelector("#pu-result").textContent = puChange < -0.5
    ? `Improved the sealed test by ${Math.abs(puChange).toFixed(1)} K`
    : puChange > 0.5
      ? `Worsened the sealed test by ${puChange.toFixed(1)} K`
      : "No meaningful gain on the sealed test";

  const tgSummary = card.dataset.polyurethane_tg_k;
  defaultTgAnchor = Number(tgSummary.median);
  polyurethaneTgAnchor = defaultTgAnchor;
  defaultTemperatureRange = {
    minimum: Math.floor(tgSummary.minimum - 20),
    maximum: Math.ceil(tgSummary.maximum + 20),
  };
  temperatureSlider.min = String(defaultTemperatureRange.minimum);
  temperatureSlider.max = String(defaultTemperatureRange.maximum);
  temperatureSlider.value = String(Math.round(defaultTgAnchor));
  temperatureSlider.disabled = false;
}

async function loadMigrationProxy() {
  const response = await fetch("/api/polly-map-proxy");
  if (!response.ok) throw new Error("Run window-light-polymer-literature-proxy to generate the PALS proxy.");
  palsProxyArtifact = await response.json();
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    state.mode = button.dataset.mode;
    state.heated = false;
    modeButtons.forEach((candidate) => {
      const selected = candidate === button;
      candidate.classList.toggle("active", selected);
      candidate.setAttribute("aria-pressed", String(selected));
    });
    render();
    configureThermalRange();
    updateThermalProxy();
  });
});

heatButton.addEventListener("click", () => {
  state.heated = !state.heated;
  render();
});

segmentSelect.addEventListener("change", () => {
  state.segment = segmentSelect.value;
  render();
  configureThermalRange();
  updateThermalProxy();
});

temperatureSlider.addEventListener("input", updateThermalProxy);
additiveSizeInput.addEventListener("input", updateThermalProxy);

render();
async function initializeModels() {
  try {
    await loadModelCard();
  } catch (error) {
    document.querySelector("#pu-mae-base").textContent = "Unavailable";
    document.querySelector("#pu-mae-tuned").textContent = "Unavailable";
    document.querySelector("#general-mae-delta").textContent = "Unavailable";
    document.querySelector("#pu-result").textContent = error.message;
  }
  try {
    await loadMigrationProxy();
  } catch (error) {
    palsProxyArtifact = null;
    mapStatusCopy.textContent = error.message;
  }
  configureThermalRange();
  updateThermalProxy();
}

initializeModels();
