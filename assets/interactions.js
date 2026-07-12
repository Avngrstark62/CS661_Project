/*
 * VentureScope — Global chart interaction layer
 *
 * Applies one consistent interaction model to every Plotly figure in the app:
 *   • Pie/Donut  : hovered slice pops out (pull) + others fade; the center
 *                  annotation updates with the hovered sector's name & value.
 *   • Bar (1 trace) / bubble maps : hovered element stays vivid, others dim.
 *   • Multi-series line/bar charts: hovered series stays vivid, others dim.
 *   • Legends    : hovering a legend item highlights the matching element
 *                  exactly like hovering the element itself (click = native
 *                  Plotly toggle, double-click = isolate).
 *   • Click      : locks the highlight until clicked again / double-click.
 *
 * No figure data is modified server-side — everything restores on unhover.
 */
(function () {
    "use strict";

    var DIM_TRACE = 0.25;      // opacity for de-emphasized series
    var DIM_POINT = 0.35;      // opacity for de-emphasized points/bars
    var PIE_DIM_ALPHA = 0.30;  // alpha for faded pie slices
    var PIE_PULL = 0.07;       // popout distance for hovered slice

    // ── helpers ─────────────────────────────────────────────
    function toRGBA(color, alpha) {
        if (!color) return "rgba(150,150,150," + alpha + ")";
        color = String(color).trim();
        if (color[0] === "#") {
            var hex = color.slice(1);
            if (hex.length === 3) hex = hex.replace(/./g, function (c) { return c + c; });
            var n = parseInt(hex, 16);
            return "rgba(" + ((n >> 16) & 255) + "," + ((n >> 8) & 255) + "," + (n & 255) + "," + alpha + ")";
        }
        var m = color.match(/rgba?\(([^)]+)\)/);
        if (m) {
            var p = m[1].split(",").map(function (s) { return parseFloat(s); });
            return "rgba(" + p[0] + "," + p[1] + "," + p[2] + "," + alpha + ")";
        }
        return color;
    }

    function fmtMoney(v) {
        if (v == null || isNaN(v)) return "";
        if (v >= 1e12) return "$" + (v / 1e12).toFixed(1) + "T";
        if (v >= 1e9) return "$" + (v / 1e9).toFixed(1) + "B";
        if (v >= 1e6) return "$" + (v / 1e6).toFixed(1) + "M";
        if (v >= 1e3) return "$" + (v / 1e3).toFixed(0) + "K";
        return "$" + Math.round(v);
    }

    function visibleCartesian(gd) {
        return (gd._fullData || []).filter(function (t) {
            return t.visible !== false && t.visible !== "legendonly" &&
                ["scatter", "bar", "histogram"].indexOf(t.type) !== -1;
        });
    }

    // ── snapshot / restore ──────────────────────────────────
    function snapshot(gd) {
        if (gd.__vsSnap) return;
        var snap = { traces: [], centerText: null };
        (gd._fullData || []).forEach(function (t, i) {
            var raw = (gd.data && gd.data[i]) || {};
            snap.traces.push({
                type: t.type,
                opacity: raw.opacity !== undefined ? raw.opacity : 1,
                markerOpacity: raw.marker && raw.marker.opacity !== undefined ? raw.marker.opacity : null,
                pieColors: t.type === "pie" && t.marker && t.marker.colors
                    ? t.marker.colors.slice() : null,
                piePull: t.type === "pie"
                    ? (Array.isArray(raw.pull) ? raw.pull.slice() : (raw.pull || 0)) : null,
            });
        });
        var ann = gd.layout && gd.layout.annotations;
        if (ann && ann.length > 0) snap.centerText = ann[0].text;
        gd.__vsSnap = snap;
    }

    function withBusy(gd, fn) {
        gd.__vsBusy = true;
        try { fn(); } finally {
            setTimeout(function () { gd.__vsBusy = false; }, 50);
        }
    }

    function restore(gd) {
        var snap = gd.__vsSnap;
        if (!snap) return;
        withBusy(gd, function () {
            snap.traces.forEach(function (s, i) {
                try {
                    if (s.type === "pie") {
                        var upd = { pull: [s.piePull] };
                        if (s.pieColors) upd["marker.colors"] = [s.pieColors];
                        Plotly.restyle(gd, upd, [i]);
                    } else {
                        Plotly.restyle(gd, {
                            opacity: s.opacity,
                            "marker.opacity": s.markerOpacity,
                        }, [i]);
                    }
                } catch (e) { /* chart may have been re-rendered */ }
            });
            if (snap.centerText != null) {
                try { Plotly.relayout(gd, { "annotations[0].text": snap.centerText }); } catch (e) { }
            }
        });
        gd.__vsSnap = null;
    }

    // ── highlight actions ───────────────────────────────────
    function highlightPie(gd, curve, ptIdx) {
        var trace = gd._fullData[curve];
        if (!trace) return;
        snapshot(gd);
        var n = (trace.values || trace.labels || []).length;
        var origColors = gd.__vsSnap.traces[curve].pieColors || [];
        var pulls = [], colors = [];
        for (var i = 0; i < n; i++) {
            pulls.push(i === ptIdx ? PIE_PULL : 0);
            var c = origColors[i % origColors.length];
            colors.push(i === ptIdx ? c : toRGBA(c, PIE_DIM_ALPHA));
        }
        withBusy(gd, function () {
            try {
                Plotly.restyle(gd, { pull: [pulls], "marker.colors": [colors] }, [curve]);
            } catch (e) { }
            // Dynamic center info for donut charts with a center annotation
            var ann = gd.layout && gd.layout.annotations;
            if (ann && ann.length > 0 && trace.hole > 0) {
                var label = trace.labels ? trace.labels[ptIdx] : "";
                var val = trace.values ? trace.values[ptIdx] : null;
                var total = 0;
                (trace.values || []).forEach(function (v) { total += v || 0; });
                var pct = total > 0 ? (val / total * 100).toFixed(1) + "%" : "";
                var short = String(label).length > 20 ? String(label).slice(0, 19) + "…" : label;
                try {
                    Plotly.relayout(gd, {
                        "annotations[0].text":
                            "<b>" + short + "</b><br>" + fmtMoney(val) + " · " + pct,
                    });
                } catch (e) { }
            }
        });
    }

    function highlightBarPoint(gd, curve, ptIdx) {
        var trace = gd._fullData[curve];
        if (!trace) return;
        var n = (trace.x && trace.x.length) || (trace.lat && trace.lat.length) || 0;
        if (!n) return;
        snapshot(gd);
        var op = [];
        for (var i = 0; i < n; i++) op.push(i === ptIdx ? 1 : DIM_POINT);
        withBusy(gd, function () {
            try { Plotly.restyle(gd, { "marker.opacity": [op] }, [curve]); } catch (e) { }
        });
    }

    function highlightTrace(gd, curve) {
        snapshot(gd);
        withBusy(gd, function () {
            (gd._fullData || []).forEach(function (t, i) {
                if (["scatter", "bar", "histogram"].indexOf(t.type) === -1) return;
                try { Plotly.restyle(gd, { opacity: i === curve ? 1 : DIM_TRACE }, [i]); } catch (e) { }
            });
        });
    }

    function applyHighlight(gd, curve, ptIdx) {
        var trace = gd._fullData && gd._fullData[curve];
        if (!trace) return;
        if (trace.type === "pie") {
            highlightPie(gd, curve, ptIdx);
        } else if (trace.type === "scattergeo" ||
            (trace.type === "bar" && visibleCartesian(gd).length === 1)) {
            if (ptIdx != null) highlightBarPoint(gd, curve, ptIdx);
        } else if (visibleCartesian(gd).length > 1) {
            highlightTrace(gd, curve);
        }
        // single-trace lines, choropleth, treemap, heatmap: native hover only
    }

    // ── event wiring ────────────────────────────────────────
    function bindGraph(gd) {
        if (!gd || gd.__vsBound || typeof gd.on !== "function" || !gd._fullData) return;
        gd.__vsBound = true;

        gd.on("plotly_hover", function (ev) {
            if (gd.__vsLocked) return;
            if (!ev.points || ev.points.length !== 1) return; // skip unified hover
            var pt = ev.points[0];
            applyHighlight(gd, pt.curveNumber, pt.pointNumber);
        });

        gd.on("plotly_unhover", function () {
            if (gd.__vsLocked) return;
            restore(gd);
        });

        gd.on("plotly_click", function (ev) {
            if (!ev.points || ev.points.length < 1) return;
            var pt = ev.points[0];
            var key = pt.curveNumber + ":" + pt.pointNumber;
            if (gd.__vsLocked === key) {          // click again → unlock
                gd.__vsLocked = null;
                restore(gd);
            } else {                               // lock the selection
                if (gd.__vsLocked) restore(gd);
                gd.__vsLocked = key;
                applyHighlight(gd, pt.curveNumber, pt.pointNumber);
            }
        });

        gd.on("plotly_doubleclick", function () {
            gd.__vsLocked = null;
            restore(gd);
        });

        // When Dash pushes a new figure (year slider, dropdowns), drop stale state
        gd.on("plotly_afterplot", function () {
            if (gd.__vsBusy) return;
            gd.__vsSnap = null;
            gd.__vsLocked = null;
        });

        // Legend hover ⇒ same highlight as hovering the element itself
        gd.addEventListener("mouseover", function (e) {
            var item = e.target && e.target.closest && e.target.closest(".legend .traces");
            if (!item || gd.__vsLocked) return;
            try {
                var d = item.__data__ && item.__data__[0];
                if (!d) return;
                if (d.trace && d.trace.type === "pie") {
                    var idx = (d.trace.labels || []).indexOf(d.label);
                    if (idx !== -1) applyHighlight(gd, d.trace.index, idx);
                } else if (d.trace && d.trace.index !== undefined) {
                    applyHighlight(gd, d.trace.index, null);
                }
            } catch (err) { /* legend datum shape changed — ignore */ }
        });
        gd.addEventListener("mouseout", function (e) {
            var item = e.target && e.target.closest && e.target.closest(".legend .traces");
            if (!item || gd.__vsLocked) return;
            restore(gd);
        });
    }

    // Dash renders graphs asynchronously — keep scanning for new ones
    setInterval(function () {
        if (typeof Plotly === "undefined") return;
        var graphs = document.querySelectorAll(".js-plotly-plot");
        for (var i = 0; i < graphs.length; i++) bindGraph(graphs[i]);
    }, 600);
})();
