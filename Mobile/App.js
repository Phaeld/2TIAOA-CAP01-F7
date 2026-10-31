// Adapted from the phase-four Expo upload flow; now uses the shared phase-seven API.
import React, { useEffect, useState, useCallback } from "react";
import {
  ActivityIndicator,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import * as ImagePicker from "expo-image-picker";
import * as SecureStore from "expo-secure-store";

const BASE = (process.env.EXPO_PUBLIC_API_URL || "").replace(/\/$/, "");
const names = {
  LOW: "Baixo",
  HIGH: "Alto",
  MEDIUM: "Atenção",
  NORMAL: "Normal",
  CRITICAL: "Crítico",
};
function Button({ children, onPress, disabled, secondary }) {
  return (
    <TouchableOpacity
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      style={[s.button, secondary && s.secondary, disabled && { opacity: 0.5 }]}
    >
      <Text style={[s.buttonText, secondary && { color: "#176953" }]}>
        {children}
      </Text>
    </TouchableOpacity>
  );
}

export default function App() {
  const [token, setToken] = useState(null),
    [loaded, setLoaded] = useState(false),
    [email, setEmail] = useState("demo@cardioia.local"),
    [password, setPassword] = useState(""),
    [tab, setTab] = useState("Painel"),
    [data, setData] = useState(null),
    [error, setError] = useState(""),
    [connectionError, setConnectionError] = useState(""),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState(""),
    [reply, setReply] = useState(null),
    [image, setImage] = useState(null),
    [vision, setVision] = useState(null);
  useEffect(() => {
    SecureStore.getItemAsync("cardioia-token")
      .then(setToken)
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);
  const logout = useCallback(async () => {
    await SecureStore.deleteItemAsync("cardioia-token");
    setToken(null);
    setData(null);
    setReply(null);
    setImage(null);
    setVision(null);
    setError("");
    setConnectionError("");
    setPassword("");
  }, []);
  const request = useCallback(
    async (path, { body, method = "GET", signal } = {}) => {
      if (!BASE)
        throw new Error(
          "Configure EXPO_PUBLIC_API_URL com a URL HTTPS do backend e refaça o build.",
        );
      const form = body instanceof FormData;
      const res = await fetch(BASE + path, {
        method,
        signal,
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(!form && body ? { "Content-Type": "application/json" } : {}),
        },
        body: body ? (form ? body : JSON.stringify(body)) : undefined,
      });
      const result = await res.json();
      if (!res.ok) {
        if (res.status === 401 && token) await logout();
        throw new Error(
          typeof result.detail === "string"
            ? result.detail
            : "Confira os dados e tente novamente.",
        );
      }
      return result;
    },
    [token, logout],
  );
  useEffect(() => {
    if (!token) return;
    let stopped = false,
      timer,
      controller;
    async function poll() {
      controller = new AbortController();
      try {
        const result = await request("/api/v1/dashboard", {
          signal: controller.signal,
        });
        if (!stopped) {
          setData(result);
          setConnectionError("");
        }
      } catch (e) {
        if (!stopped) setConnectionError(e.message);
      }
      if (!stopped) timer = setTimeout(poll, 5000);
    }
    poll();
    return () => {
      stopped = true;
      clearTimeout(timer);
      controller?.abort();
    };
  }, [token, request]);
  async function act(fn) {
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function login() {
    const result = await request("/api/v1/auth/login", {
      method: "POST",
      body: { email, password },
    });
    await SecureStore.setItemAsync("cardioia-token", result.access_token);
    setToken(result.access_token);
    setPassword("");
  }
  async function pick() {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      quality: 1,
    });
    if (!result.canceled) {
      setImage(result.assets[0]);
      setVision(null);
    }
  }
  async function analyze() {
    const form = new FormData();
    form.append("image", {
      uri: image.uri,
      name: image.fileName || "raiox.jpg",
      type: image.mimeType || "image/jpeg",
    });
    setVision(await request("/api/v1/vision", { method: "POST", body: form }));
  }
  if (!loaded)
    return (
      <SafeAreaView style={s.safe}>
        <ActivityIndicator />
      </SafeAreaView>
    );
  const latest = data?.latest;
  return (
    <SafeAreaView style={s.safe}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <ScrollView
          contentContainerStyle={s.container}
          keyboardShouldPersistTaps="handled"
        >
          <View style={s.header}>
            <Text style={s.brand}>♡ CardioIA</Text>
            {token && (
              <TouchableOpacity onPress={logout} accessibilityRole="button">
                <Text style={s.link}>Sair</Text>
              </TouchableOpacity>
            )}
          </View>
          <Text style={s.eyebrow}>FIAP · PLATAFORMA INTEGRADA</Text>
          {!token ? (
            <>
              <Text style={s.title}>
                Conectar sinais.{"\n"}Compreender o contexto.
              </Text>
              <Text style={s.subtitle}>
                Entre no ambiente acadêmico de demonstração.
              </Text>
              <View style={s.card}>
                <Text style={s.label}>E-mail</Text>
                <TextInput
                  accessibilityLabel="E-mail"
                  style={s.input}
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  autoComplete="email"
                  keyboardType="email-address"
                />
                <Text style={s.label}>Senha</Text>
                <TextInput
                  accessibilityLabel="Senha"
                  style={s.input}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  autoComplete="password"
                />
                <Button disabled={busy || !password} onPress={() => act(login)}>
                  Acessar plataforma
                </Button>
              </View>
            </>
          ) : (
            <>
              <Text style={s.title}>Sua visão integrada.</Text>
              <View style={s.tabs}>
                {["Painel", "Assistente", "Imagem"].map((t) => (
                  <TouchableOpacity
                    key={t}
                    onPress={() => setTab(t)}
                    style={[s.tab, t === tab && s.tabActive]}
                    accessibilityRole="button"
                  >
                    <Text
                      style={
                        t === tab
                          ? { color: "#087c6b", fontWeight: "700" }
                          : { color: "#70847f" }
                      }
                    >
                      {t}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
              {tab === "Painel" && (
                <>
                  <Text style={s.subtitle}>
                    {!data || data.stale || connectionError
                      ? "Sem leitura recente · aguardando sensor"
                      : "Recebendo sinais · atualização a cada 5 s"}
                  </Text>
                  <View style={s.grid}>
                    <View style={s.metric}>
                      <Text style={s.label}>Batimentos</Text>
                      <Text style={s.value}>
                        {latest?.vitals.heart_rate_bpm ?? "—"}{" "}
                        <Text style={s.unit}>bpm</Text>
                      </Text>
                    </View>
                    <View style={s.metric}>
                      <Text style={s.label}>Temperatura</Text>
                      <Text style={s.value}>
                        {latest?.vitals.temperature_c?.toFixed(1) ?? "—"}{" "}
                        <Text style={s.unit}>°C</Text>
                      </Text>
                    </View>
                  </View>
                  <View style={s.card}>
                    <Text style={s.label}>RISCO OPERACIONAL SIMULADO</Text>
                    <Text style={s.value}>
                      {latest
                        ? `${(latest.prediction.risk_probability * 100).toFixed(1)}%`
                        : "—"}
                    </Text>
                    <Text style={s.subtitle}>
                      {latest
                        ? names[latest.prediction.risk_level]
                        : "Aguardando primeira leitura"}
                    </Text>
                    <Text style={s.small}>
                      Modelo da fase 6. Este indicador usa contexto hospitalar
                      sintético e não representa risco individual de infarto.
                    </Text>
                  </View>
                  <View style={s.card}>
                    <Text style={s.cardTitle}>Alertas do sensor</Text>
                    <Text style={s.subtitle}>
                      {latest
                        ? names[latest.sensor_alerts.risk_level]
                        : "Sem leitura"}
                    </Text>
                    {latest?.sensor_alerts.alerts.map((a) => (
                      <Text key={a.type} style={s.alert}>
                        {a.message}
                      </Text>
                    ))}
                    {latest && !latest.sensor_alerts.alerts.length && (
                      <Text style={s.small}>
                        Nenhuma regra de alerta acionada.
                      </Text>
                    )}
                    <Text style={s.small}>
                      LED Wokwi: {latest?.feedback.led || "—"}
                    </Text>
                  </View>
                  <View style={s.card}>
                    <Text style={s.cardTitle}>Demonstração</Text>
                    <Button
                      disabled={busy}
                      secondary
                      onPress={() =>
                        act(async () => {
                          await request(
                            "/api/v1/demo/reading?scenario=normal",
                            { method: "POST" },
                          );
                          setData(await request("/api/v1/dashboard"));
                        })
                      }
                    >
                      Enviar leitura normal
                    </Button>
                    <Button
                      disabled={busy}
                      secondary
                      onPress={() =>
                        act(async () => {
                          await request("/api/v1/demo/reading?scenario=alert", {
                            method: "POST",
                          });
                          setData(await request("/api/v1/dashboard"));
                        })
                      }
                    >
                      Simular alerta
                    </Button>
                  </View>
                  <View style={s.card}>
                    <Text style={s.cardTitle}>Últimas leituras</Text>
                    {data?.history?.slice(0, 8).map((r) => (
                      <View style={s.history} key={r.event_id}>
                        <Text style={s.small}>
                          {new Date(r.captured_at).toLocaleTimeString("pt-BR")}
                        </Text>
                        <Text style={s.small}>
                          {r.vitals.heart_rate_bpm} bpm ·{" "}
                          {r.vitals.temperature_c} °C
                        </Text>
                      </View>
                    ))}
                  </View>
                </>
              )}
              {tab === "Assistente" && (
                <View style={s.card}>
                  <Text style={s.cardTitle}>Converse sobre a simulação</Text>
                  <Text style={s.small}>
                    A pergunta usa a última leitura e trechos da base da fase 1.
                    Não há memória de conversa.
                  </Text>
                  <TextInput
                    accessibilityLabel="Pergunta ao assistente"
                    style={[s.input, { height: 100, textAlignVertical: "top" }]}
                    multiline
                    value={message}
                    onChangeText={setMessage}
                    maxLength={4000}
                    placeholder="O que significa o risco operacional?"
                  />
                  <Button
                    disabled={busy || message.trim().length < 3}
                    onPress={() =>
                      act(async () =>
                        setReply(
                          await request("/api/v1/chat", {
                            method: "POST",
                            body: { message },
                          }),
                        ),
                      )
                    }
                  >
                    Enviar pergunta
                  </Button>
                  {reply && (
                    <View style={s.response}>
                      <Text style={s.eyebrow}>
                        {reply.source === "gemini"
                          ? "GEMINI"
                          : "RESPOSTA LOCAL · GEMINI NÃO CONFIGURADO"}
                      </Text>
                      <Text style={s.body}>{reply.reply}</Text>
                    </View>
                  )}
                </View>
              )}
              {tab === "Imagem" && (
                <View style={s.card}>
                  <Text style={s.cardTitle}>Radiografia de tórax</Text>
                  <Text style={s.small}>
                    Modelo real da fase 4 · ResNet50 + Grad-CAM
                  </Text>
                  {!data?.vision_enabled && (
                    <Text style={s.small}>
                      Análise de imagens disponível na versão local. Hospedagem
                      deste módulo prevista para uma próxima etapa.
                    </Text>
                  )}
                  <Button
                    secondary
                    disabled={busy || !data?.vision_enabled}
                    onPress={() => act(pick)}
                  >
                    Selecionar radiografia de teste
                  </Button>
                  {image && (
                    <Image
                      source={{ uri: image.uri }}
                      style={s.image}
                      resizeMode="contain"
                    />
                  )}
                  {image && (
                    <Button disabled={busy} onPress={() => act(analyze)}>
                      Analisar imagem
                    </Button>
                  )}
                  {vision && (
                    <>
                      <Text style={s.body}>
                        Classe estimada: {vision.classe}
                      </Text>
                      <Text style={s.small}>
                        P(cardiomegalia):{" "}
                        {(vision.prob_cardiomegalia * 100).toFixed(1)}%
                      </Text>
                      <Image
                        source={{ uri: vision.gradcam_png_b64 }}
                        style={s.image}
                        resizeMode="contain"
                      />
                    </>
                  )}
                </View>
              )}
            </>
          )}
          {busy && <ActivityIndicator color="#087c6b" style={{ margin: 15 }} />}
          {!!connectionError && (
            <Text accessibilityRole="alert" style={s.error}>
              {connectionError}
            </Text>
          )}
          {!!error && (
            <Text accessibilityRole="alert" style={s.error}>
              {error}
            </Text>
          )}
          <Text style={s.footer}>
            Protótipo acadêmico · Somente dados simulados. Não é diagnóstico nem
            orientação médica.
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f4f6f3" },
  container: { padding: 22, paddingTop: 30, paddingBottom: 40 },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 28,
  },
  brand: { fontSize: 27, fontWeight: "800", color: "#164b3f" },
  link: { color: "#087c6b", padding: 10 },
  eyebrow: {
    fontSize: 10,
    color: "#78927c",
    letterSpacing: 1.2,
    fontWeight: "700",
  },
  title: {
    fontSize: 29,
    fontWeight: "700",
    color: "#183f35",
    marginTop: 15,
    marginBottom: 15,
    letterSpacing: -0.7,
  },
  subtitle: {
    fontSize: 13,
    color: "#70847f",
    lineHeight: 21,
    marginBottom: 14,
  },
  card: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#e2e9e4",
    padding: 20,
    borderRadius: 14,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: "600",
    color: "#213b3a",
    marginBottom: 14,
  },
  label: { fontSize: 11, color: "#70847f", marginBottom: 9 },
  input: {
    borderWidth: 1,
    borderColor: "#d9e2da",
    padding: 13,
    borderRadius: 8,
    color: "#213b3a",
    backgroundColor: "#fbfcfa",
    marginBottom: 20,
    marginTop: 6,
  },
  button: {
    backgroundColor: "#087c6b",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },
  secondary: { backgroundColor: "#edf4ee" },
  buttonText: { color: "#fff", fontWeight: "600", fontSize: 13 },
  tabs: { flexDirection: "row", gap: 6, marginBottom: 22 },
  tab: { padding: 12, flex: 1, alignItems: "center", borderRadius: 8 },
  tabActive: { backgroundColor: "#e3efe5" },
  grid: { flexDirection: "row", gap: 12, marginBottom: 16 },
  metric: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 17,
    borderWidth: 1,
    borderColor: "#e2e9e4",
    borderRadius: 12,
  },
  value: {
    fontSize: 31,
    fontWeight: "600",
    color: "#164638",
    marginVertical: 8,
  },
  unit: { fontSize: 12, color: "#91a395" },
  small: { fontSize: 11, color: "#7e9082", lineHeight: 18 },
  alert: { fontSize: 12, color: "#a65441", lineHeight: 20, marginBottom: 8 },
  history: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#eff3ec",
  },
  response: {
    backgroundColor: "#eef4ec",
    padding: 16,
    borderRadius: 8,
    marginTop: 20,
  },
  body: { fontSize: 14, color: "#355f47", lineHeight: 23, marginTop: 10 },
  image: {
    width: "100%",
    height: 240,
    backgroundColor: "#0c2222",
    borderRadius: 9,
    marginTop: 15,
  },
  error: {
    color: "#a03d30",
    backgroundColor: "#ffede8",
    padding: 15,
    borderRadius: 8,
    lineHeight: 20,
  },
  footer: {
    fontSize: 10,
    color: "#91a08e",
    lineHeight: 17,
    textAlign: "center",
    marginTop: 24,
  },
});
