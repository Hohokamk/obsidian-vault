window.__ModuleLoader__.load({ id: "billion-context", factory: (require) => {
var module = { exports: {} };
var exports = module.exports;

"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/agent/dsh-native-client.ts
var dsh_native_client_exports = {};
__export(dsh_native_client_exports, {
  apply: () => apply,
  inject: () => inject
});
module.exports = __toCommonJS(dsh_native_client_exports);
var import_react = require("react");
var inject = ["slots", "locale"];
var NS = "bili";
var ORIGIN_PATH = "/bili/origin";
var POLL_INTERVAL_MS = 3e3;
var POLL_MAX_ATTEMPTS = 10;
var SLOW_POLL_INTERVAL_MS = 1e4;
var zh = {
  "nav": "bili\u8BBE\u7F6E",
  "title": "billion-context \u538B\u7F29\u4EE3\u7406",
  "open": "\u6253\u5F00 Web UI",
  "hint": "\u67E5\u770B\u538B\u7F29\u72B6\u6001\u3001\u4F1A\u8BDD\u4E0E\u4E0A\u4E0B\u6587\u7A97\u53E3\u3002",
  "degraded": "\u5F53\u524D dsh \u8FDB\u7A0B\u672A\u7ED1\u5B9A bili \u4EE3\u7406\uFF08\u672A\u7ECF bili dsh \u542F\u52A8\uFF0C\u6216\u4EE3\u7406\u5C1A\u672A\u5C31\u7EEA\uFF09\u2014\u2014\u5148\u8FD0\u884C /acp\uFF0C\u6216\u6539\u7528 bili dsh \u542F\u52A8\u3002"
};
var en = {
  "nav": "bili",
  "title": "billion-context compression proxy",
  "open": "Open Web UI",
  "hint": "Inspect compression status, sessions and context windows.",
  "degraded": "This dsh process is not bound to a bili proxy (not launched via bili dsh, or the proxy is not up yet) \u2014 run /acp first, or launch through bili dsh."
};
function readOrigin() {
  const g = globalThis;
  const origin = g.__BILI__?.origin;
  return typeof origin === "string" && origin.length > 0 ? origin : void 0;
}
function openExternal(url) {
  const w = globalThis;
  if (typeof w.open === "function") w.open(url, "_blank", "noopener,noreferrer");
}
function probeOrigin(onOrigin) {
  if (typeof fetch !== "function") return () => {
  };
  let cancelled = false;
  let timer;
  let attempts = 0;
  const poll = async () => {
    let resolved = false;
    try {
      const res = await fetch(ORIGIN_PATH);
      if (res.ok) {
        const data = await res.json();
        if (typeof data.origin === "string" && data.origin.length > 0 && !cancelled) {
          onOrigin(data.origin);
          resolved = true;
        }
      }
    } catch {
    }
    if (resolved) return;
    attempts += 1;
    const delay = attempts < POLL_MAX_ATTEMPTS ? POLL_INTERVAL_MS : SLOW_POLL_INTERVAL_MS;
    if (!cancelled) timer = setTimeout(() => void poll(), delay);
  };
  void poll();
  return () => {
    cancelled = true;
    if (timer !== void 0) clearTimeout(timer);
  };
}
function apply(ctx) {
  const zhDict = zh;
  const enDict = en;
  ctx.effect(
    () => ctx.locale.register(NS, { zh: zhDict, en: enDict }),
    "bili: dictionaries"
  );
  const t = ctx.locale.bind(NS);
  const panel = (titled) => () => {
    const [origin, setOrigin] = (0, import_react.useState)(readOrigin());
    (0, import_react.useEffect)(() => {
      if (origin !== void 0) return;
      return probeOrigin(setOrigin);
    }, [origin]);
    return (0, import_react.createElement)(
      "div",
      { style: { display: "flex", flexDirection: "column", gap: 12, padding: "20px 8px" } },
      titled ? (0, import_react.createElement)("h3", { style: { margin: 0, fontSize: 16, fontWeight: 600 } }, t("title")) : null,
      origin === void 0 ? (0, import_react.createElement)("p", { style: { margin: 0, opacity: 0.7, lineHeight: 1.6 } }, t("degraded")) : (0, import_react.createElement)(
        "button",
        {
          type: "button",
          onClick: () => openExternal(`${origin}/__bili/`),
          style: {
            alignSelf: "flex-start",
            cursor: "pointer",
            borderRadius: 8,
            border: "1px solid rgba(127,127,127,0.4)",
            background: "transparent",
            color: "inherit",
            fontFamily: "inherit",
            fontSize: 14,
            lineHeight: "22px",
            padding: "7px 16px"
          }
        },
        `${t("open")}\uFF08${origin}\uFF09`
      ),
      (0, import_react.createElement)("p", { style: { margin: 0, opacity: 0.7, fontSize: 13, lineHeight: 1.6 } }, t("hint"))
    );
  };
  ctx.slots.inject(
    "settings.section",
    () => ctx.slots.register({ name: "settings.section", id: "bili", order: 100, label: () => t("nav"), locale: NS }, panel(true))
  );
  ctx.slots.inject(
    "plugins.bundle.config",
    () => ctx.slots.register({ name: "plugins.bundle.config", key: "billion-context", locale: NS }, panel(false))
  );
}

return module.exports;
}});
