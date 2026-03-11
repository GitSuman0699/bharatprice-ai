"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { sendChat, ChatResponse } from "@/lib/api";

interface Message {
    id: string;
    text: string;
    sender: "user" | "bot";
    timestamp: Date;
}

const LANGUAGES = [
    { code: "en", label: "English" },
    { code: "hi", label: "हिंदी" },
];

const CITIES = [
    { id: "delhi", name: "Delhi", nameHi: "दिल्ली", icon: "🏛️" },
    { id: "mumbai", name: "Mumbai", nameHi: "मुंबई", icon: "🌊" },
    { id: "bangalore", name: "Bangalore", nameHi: "बैंगलोर", icon: "💻" },
    { id: "kolkata", name: "Kolkata", nameHi: "कोलकाता", icon: "🌉" },
    { id: "chennai", name: "Chennai", nameHi: "चेन्नई", icon: "🛕" },
    { id: "hyderabad", name: "Hyderabad", nameHi: "हैदराबाद", icon: "🕌" },
    { id: "jaipur", name: "Jaipur", nameHi: "जयपुर", icon: "🏰" },
    { id: "lucknow", name: "Lucknow", nameHi: "लखनऊ", icon: "🕌" },
];

const CONTENT = {
    en: {
        welcome: (city: string) => `🙏 **Welcome to BharatPrice AI!**

I'm your AI-powered pricing assistant for smart kirana store management.
📍 Showing prices for **${city}**

Ask me about any product's price, and I'll give you:
✅ Today's recommended selling price
📊 Competitor price comparison
🏪 Wholesale mandi rates
📈 Price trends and forecasts

_Try the suggestions below to get started!_`,
        suggestions: [
            "What is the price of atta today?",
            "Compare tomato prices",
            "Mandi rates for onion",
            "Price trend of rice",
            "Show all products",
        ],
        placeholder: "Ask about any product price...",
        online: "● Online — Powered by AWS Bedrock",
        regionTitle: "Select Your City",
        regionSubtitle: "We'll show prices specific to your area",
        detectBtn: "📍 Detect My Location",
        detecting: "Detecting...",
        continueBtn: "Continue →",
    },
    hi: {
        welcome: (city: string) => `🙏 **नमस्ते! BharatPrice AI में आपका स्वागत है!**

मैं आपका AI-संचालित मूल्य निर्धारण सहायक हूँ, जो आपकी किराना दुकान को स्मार्ट बनाने में मदद करता है।
📍 **${city}** के लिए कीमतें दिखा रहा हूँ

किसी भी प्रोडक्ट की कीमत पूछें, मैं बताऊंगा:
✅ आज की सुझाई गई बिक्री कीमत
📊 प्रतिस्पर्धी मूल्य तुलना
🏪 थोक मंडी भाव
📈 मूल्य रुझान और पूर्वानुमान

_शुरू करने के लिए नीचे दिए गए सुझाव आज़माएं!_`,
        suggestions: [
            "आज आटे का रेट क्या है?",
            "टमाटर की कीमत तुलना करो",
            "प्याज़ की मंडी रेट बताओ",
            "चावल का प्राइस ट्रेंड दिखाओ",
            "सभी प्रोडक्ट दिखाओ",
        ],
        placeholder: "कोई भी प्रोडक्ट का रेट पूछें...",
        online: "● ऑनलाइन — AWS Bedrock द्वारा संचालित",
        regionTitle: "अपना शहर चुनें",
        regionSubtitle: "हम आपके क्षेत्र की कीमतें दिखाएंगे",
        detectBtn: "📍 मेरा लोकेशन पता करें",
        detecting: "पता लगा रहे हैं...",
        continueBtn: "आगे बढ़ें →",
    },
} as Record<string, {
    welcome: (city: string) => string;
    suggestions: string[];
    placeholder: string;
    online: string;
    regionTitle: string;
    regionSubtitle: string;
    detectBtn: string;
    detecting: string;
    continueBtn: string;
}>;

const LANG_STORAGE_KEY = "bharatprice-language";
const REGION_STORAGE_KEY = "bharatprice-region";
const PINCODE_STORAGE_KEY = "bharatprice-pincode";
const STATE_STORAGE_KEY = "bharatprice-state";
const DISTRICT_STORAGE_KEY = "bharatprice-district";
const CITY_NAME_STORAGE_KEY = "bharatprice-custom-city";

// Rough geo-coordinates to city mapping for geolocation
const CITY_COORDS: { id: string; lat: number; lon: number }[] = [
    { id: "delhi", lat: 28.6139, lon: 77.209 },
    { id: "mumbai", lat: 19.076, lon: 72.8777 },
    { id: "bangalore", lat: 12.9716, lon: 77.5946 },
    { id: "kolkata", lat: 22.5726, lon: 88.3639 },
    { id: "chennai", lat: 13.0827, lon: 80.2707 },
    { id: "hyderabad", lat: 17.385, lon: 78.4867 },
    { id: "jaipur", lat: 26.9124, lon: 75.7873 },
    { id: "lucknow", lat: 26.8467, lon: 80.9462 },
];

function findNearestCity(lat: number, lon: number): string {
    let minDist = Infinity;
    let nearest = "delhi";
    for (const c of CITY_COORDS) {
        const dist = Math.sqrt((c.lat - lat) ** 2 + (c.lon - lon) ** 2);
        if (dist < minDist) {
            minDist = dist;
            nearest = c.id;
        }
    }
    return nearest;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState("en");
    const [region, setRegion] = useState("");
    const [customCityName, setCustomCityName] = useState(""); // Track exact city from API
    const [pincode, setPincode] = useState("");
    const [locationState, setLocationState] = useState("");
    const [locationDistrict, setLocationDistrict] = useState("");
    const [pincodeInput, setPincodeInput] = useState("");
    const [showRegionPicker, setShowRegionPicker] = useState(false);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [isDetecting, setIsDetecting] = useState(false);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognitionRef = useRef<any>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const getContent = (lang: string) => CONTENT[lang] || CONTENT.en;
    const getCityName = (regionId: string, lang: string) => {
        if (customCityName) return customCityName;
        const city = CITIES.find(c => c.id === regionId);
        if (!city) return "Delhi";
        return lang === "hi" ? city.nameHi : city.name;
    };

    // Load saved prefs on mount
    useEffect(() => {
        // Hide "Try Demo" from navbar when on chat page
        document.body.classList.add("chat-active");

        const savedLang = localStorage.getItem(LANG_STORAGE_KEY) || "en";
        const savedRegion = localStorage.getItem(REGION_STORAGE_KEY);
        const savedPincode = localStorage.getItem(PINCODE_STORAGE_KEY);
        const savedState = localStorage.getItem(STATE_STORAGE_KEY);
        const savedDistrict = localStorage.getItem(DISTRICT_STORAGE_KEY);
        const savedCustomCity = localStorage.getItem(CITY_NAME_STORAGE_KEY);
        setLanguage(savedLang);

        if (savedState) setLocationState(savedState);
        if (savedDistrict) setLocationDistrict(savedDistrict);

        if (savedPincode) {
            setPincode(savedPincode);
            setPincodeInput(savedPincode);
        }

        if (savedRegion) {
            // Region was already selected previously
            setRegion(savedRegion);
            if (savedCustomCity) setCustomCityName(savedCustomCity);

            const c = getContent(savedLang);
            const cityName = savedCustomCity || getCityName(savedRegion, savedLang);
            const displayName = savedPincode
                ? `${cityName} (📌 ${savedPincode})`
                : cityName;
            setMessages([{
                id: "welcome", sender: "bot", timestamp: new Date(),
                text: c.welcome(displayName),
            }]);
            setSuggestions(c.suggestions);
        } else {
            // First visit — show region picker
            setShowRegionPicker(true);
        }

        return () => { document.body.classList.remove("chat-active"); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const selectRegion = async (regionId: string) => {
        // Save pincode
        const pc = pincodeInput.trim();
        if (pc && /^\d{6}$/.test(pc)) {
            setPincode(pc);
            localStorage.setItem(PINCODE_STORAGE_KEY, pc);

            // Use India Post API for accurate Indian pincode → city resolution
            try {
                const postResp = await fetch(`https://api.postalpincode.in/pincode/${pc}`);
                if (postResp.ok) {
                    const postData = await postResp.json();
                    if (postData?.[0]?.Status === "Success" && postData[0].PostOffice?.length > 0) {
                        // Pick the Head Post Office or first entry
                        const hpo = postData[0].PostOffice.find((po: any) => po.BranchType === "Head Post Office")
                            || postData[0].PostOffice[0];
                        const cityName = hpo.Block !== "NA" ? hpo.Block : (hpo.Name || hpo.Division || "");
                        const dist = hpo.District || "";
                        const st = hpo.State || "";

                        if (st) {
                            setLocationState(st);
                            localStorage.setItem(STATE_STORAGE_KEY, st);
                        }
                        if (dist) {
                            setLocationDistrict(dist);
                            localStorage.setItem(DISTRICT_STORAGE_KEY, dist);
                        }
                        if (cityName) {
                            setCustomCityName(cityName);
                            localStorage.setItem(CITY_NAME_STORAGE_KEY, cityName);
                        }

                        const resolvedRegion = cityName || regionId;
                        setRegion(resolvedRegion);
                        localStorage.setItem(REGION_STORAGE_KEY, resolvedRegion);

                        setShowRegionPicker(false);
                        const c = getContent(language);
                        const displayName = `${cityName} (📌 ${pc})`;
                        setMessages([{
                            id: "welcome", sender: "bot", timestamp: new Date(),
                            text: c.welcome(displayName),
                        }]);
                        setSuggestions(c.suggestions);
                        return; // Done!
                    }
                }
            } catch (e) {
                console.error("India Post API failed, falling back to Nominatim", e);
            }

            // Fallback: Nominatim reverse geocode
            try {
                const searchResp = await fetch(`https://nominatim.openstreetmap.org/search?postalcode=${pc}&country=india&format=json&limit=1`);
                if (searchResp.ok) {
                    const searchData = await searchResp.json();
                    if (searchData?.length > 0) {
                        const revResp = await fetch(
                            `https://nominatim.openstreetmap.org/reverse?lat=${searchData[0].lat}&lon=${searchData[0].lon}&format=json&zoom=14&addressdetails=1`,
                            { headers: { "Accept-Language": "en" } }
                        );
                        if (revResp.ok) {
                            const revData = await revResp.json();
                            const addr = revData?.address;
                            const st = addr?.state || "";
                            const dist = addr?.state_district || "";
                            const cityName = addr?.city || addr?.town || addr?.county || dist || "";

                            if (st) { setLocationState(st); localStorage.setItem(STATE_STORAGE_KEY, st); }
                            if (dist) { setLocationDistrict(dist); localStorage.setItem(DISTRICT_STORAGE_KEY, dist); }
                            if (cityName) { setCustomCityName(cityName); localStorage.setItem(CITY_NAME_STORAGE_KEY, cityName); }

                            const resolvedRegion = cityName || regionId;
                            setRegion(resolvedRegion);
                            localStorage.setItem(REGION_STORAGE_KEY, resolvedRegion);

                            setShowRegionPicker(false);
                            const c = getContent(language);
                            setMessages([{ id: "welcome", sender: "bot", timestamp: new Date(), text: c.welcome(`${cityName} (📌 ${pc})`) }]);
                            setSuggestions(c.suggestions);
                            return;
                        }
                    }
                }
            } catch (e) {
                console.error("Nominatim fallback also failed", e);
            }
        }

        // Fallback if Nominatim failed
        setRegion(regionId);
        localStorage.setItem(REGION_STORAGE_KEY, regionId);
        setShowRegionPicker(false);

        const c = getContent(language);
        setMessages([{
            id: "welcome", sender: "bot", timestamp: new Date(),
            text: c.welcome(getCityName(regionId, language)),
        }]);
        setSuggestions(c.suggestions);
    };

    const detectLocation = () => {
        if (!navigator.geolocation) {
            alert("Geolocation is not supported by your browser.");
            return;
        }
        setIsDetecting(true);
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                // First: set nearest city from coords (instant)
                const nearest = findNearestCity(pos.coords.latitude, pos.coords.longitude);
                setRegion(nearest);
                localStorage.setItem(REGION_STORAGE_KEY, nearest);

                // Then: try to reverse geocode for exact city and pincode
                try {
                    const resp = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&format=json&zoom=18&addressdetails=1`,
                        { headers: { "Accept-Language": "en" } }
                    );
                    if (resp.ok) {
                        const data = await resp.json();

                        // Extract exact city/town name
                        const exactCity = data?.address?.city || data?.address?.town || data?.address?.county || "";
                        if (exactCity) {
                            setCustomCityName(exactCity);
                            localStorage.setItem(CITY_NAME_STORAGE_KEY, exactCity);
                        } else {
                            localStorage.removeItem(CITY_NAME_STORAGE_KEY);
                        }

                        // Extract Pincode
                        const pc = data?.address?.postcode;
                        if (pc && /^\d{6}$/.test(pc)) {
                            setPincode(pc);
                            setPincodeInput(pc);
                            localStorage.setItem(PINCODE_STORAGE_KEY, pc);
                        }

                        // Extract State and District
                        const st = data?.address?.state || "";
                        const dist = data?.address?.state_district || "";
                        if (st) {
                            setLocationState(st);
                            localStorage.setItem(STATE_STORAGE_KEY, st);
                        }
                        if (dist) {
                            setLocationDistrict(dist);
                            localStorage.setItem(DISTRICT_STORAGE_KEY, dist);
                        }

                        // Show welcome message with new fetched exact data
                        setShowRegionPicker(false);
                        const c = getContent(language);
                        const displayName = pc && /^\d{6}$/.test(pc)
                            ? `${exactCity || getCityName(nearest, language)} (📌 ${pc})`
                            : exactCity || getCityName(nearest, language);
                        setMessages([{
                            id: "welcome", sender: "bot", timestamp: new Date(),
                            text: c.welcome(displayName),
                        }]);
                        setSuggestions(c.suggestions);
                    }
                } catch {
                    // Reverse geocoding failed — just use nearest city
                    setShowRegionPicker(false);
                }

                setIsDetecting(false);
            },
            () => {
                setIsDetecting(false);
                alert("Could not detect location. Please select a city manually.");
            },
            { timeout: 10000 }
        );
    };

    // When language changes: persist, reset chat
    const handleLanguageChange = (code: string) => {
        setLanguage(code);
        localStorage.setItem(LANG_STORAGE_KEY, code);

        if (region) {
            const c = getContent(code);
            setMessages([{
                id: "welcome", sender: "bot", timestamp: new Date(),
                text: c.welcome(getCityName(region, code)),
            }]);
            setSuggestions(c.suggestions);
        }
    };

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    const handleSend = async (text?: string) => {
        const messageText = text || input.trim();
        if (!messageText || isLoading) return;

        const userMsg: Message = {
            id: `user_${Date.now()}`,
            text: messageText,
            sender: "user",
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);
        setSuggestions([]);

        try {
            // Build chat history from recent messages (exclude welcome, keep last 6)
            const history = messages
                .filter(m => m.id !== "welcome")
                .slice(-6)
                .map(m => ({
                    role: m.sender === "bot" ? "assistant" : "user",
                    content: m.text,
                }));

            const payload = {
                message: messageText,
                language: language,
                region: customCityName || region,
                pincode: pincode || undefined,
                state: locationState || undefined,
                district: locationDistrict || undefined,
                chat_history: history,
            };
            console.log("SENDING TO BACKEND:", JSON.stringify(payload));
            const response: ChatResponse = await sendChat(payload);

            const botMsg: Message = {
                id: `bot_${Date.now()}`,
                text: response.reply,
                sender: "bot",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, botMsg]);

            if (response.suggestions && response.suggestions.length > 0) {
                setSuggestions(response.suggestions);
            }
        } catch {
            const errorMsg: Message = {
                id: `error_${Date.now()}`,
                text: "⚠️ Sorry, I encountered an error. Please try again in a moment. If the issue persists, the service may be temporarily unavailable.",
                sender: "bot",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMsg]);
            setSuggestions(getContent(language).suggestions);
        }

        setIsLoading(false);
        inputRef.current?.focus();
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const toggleVoice = useCallback(() => {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const win = window as any;
        if (!win.webkitSpeechRecognition && !win.SpeechRecognition) {
            alert("Voice input is not supported in your browser. Try Chrome.");
            return;
        }

        // If already recording → stop
        if (isRecording && recognitionRef.current) {
            recognitionRef.current.stop();
            return; // onend will clean up state
        }

        const SpeechRecognition = win.SpeechRecognition || win.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.lang = language === "hi" ? "hi-IN" : "en-IN";
        recognition.interimResults = true;  // show live text as user speaks
        recognition.continuous = true;      // keep listening until user stops
        recognitionRef.current = recognition;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        recognition.onresult = (event: any) => {
            let interim = "";
            let final_ = "";
            for (let i = 0; i < event.results.length; i++) {
                const result = event.results[i];
                if (result.isFinal) {
                    final_ += result[0].transcript;
                } else {
                    interim += result[0].transcript;
                }
            }
            // Show whatever we have so far in the input box
            setInput(final_ || interim);
        };

        recognition.onerror = (e: any) => {
            // "no-speech" is normal — user didn't speak yet, just keep listening
            if (e.error === "no-speech") return;
            setIsRecording(false);
            recognitionRef.current = null;
        };

        recognition.onend = () => {
            setIsRecording(false);
            recognitionRef.current = null;
        };

        setIsRecording(true);
        recognition.start();
    }, [isRecording, language]);

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    const formatText = (text: string) => {
        const parts = text.split(/(\*\*[^*]+\*\*)/g);
        return parts.map((part, i) => {
            if (part.startsWith("**") && part.endsWith("**")) {
                return <strong key={i}>{part.slice(2, -2)}</strong>;
            }
            if (part.startsWith("_") && part.endsWith("_")) {
                return <em key={i}>{part.slice(1, -1)}</em>;
            }
            return part;
        });
    };

    const content = getContent(language);

    // ─── Region Picker Overlay ─────────────────────────
    if (showRegionPicker) {
        return (
            <div className="chat-page">
                <div className="region-overlay">
                    <div className="region-picker">
                        <div className="region-picker-header">
                            <span className="region-picker-icon">📍</span>
                            <h2>{content.regionTitle}</h2>
                            <p>{content.regionSubtitle}</p>
                        </div>

                        <button
                            className="detect-location-btn"
                            onClick={detectLocation}
                            disabled={isDetecting}
                        >
                            {isDetecting ? content.detecting : content.detectBtn}
                        </button>

                        <div className="region-divider">
                            <span>{language === "hi" ? "या पिनकोड डालें" : "or enter your Pincode"}</span>
                        </div>

                        {/* Pincode input — mandatory */}
                        <div className="pincode-section">
                            <div className="pincode-input-row">
                                <input
                                    type="text"
                                    className="pincode-input"
                                    placeholder={language === "hi" ? "जैसे 734001" : "e.g. 734001"}
                                    value={pincodeInput}
                                    onChange={(e) => {
                                        const val = e.target.value.replace(/\D/g, "").slice(0, 6);
                                        setPincodeInput(val);
                                    }}
                                    maxLength={6}
                                />
                                {pincodeInput.length === 6 && (
                                    <span className="pincode-check">✅</span>
                                )}
                            </div>
                            <p className="pincode-hint">
                                {language === "hi"
                                    ? "📡 पिनकोड डालने पर data.gov.in से रियल-टाइम मंडी भाव मिलेंगे"
                                    : "📡 With pincode, you get real-time mandi prices from data.gov.in"}
                            </p>
                        </div>

                        {pincodeInput.length === 6 && (
                            <button
                                className="btn-primary region-continue-btn"
                                onClick={() => selectRegion("custom")}
                            >
                                {content.continueBtn}
                            </button>
                        )}

                        {/* Language toggle in picker too */}
                        <div className="region-lang-toggle">
                            {LANGUAGES.map((lang) => (
                                <button
                                    key={lang.code}
                                    className={`lang-btn ${language === lang.code ? "active" : ""}`}
                                    onClick={() => {
                                        setLanguage(lang.code);
                                        localStorage.setItem(LANG_STORAGE_KEY, lang.code);
                                    }}
                                >
                                    {lang.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // ─── Main Chat UI ──────────────────────────────────
    return (
        <div className="chat-page">
            <div className="chat-container">
                {/* Chat Header */}
                <div className="chat-header">
                    <div className="chat-header-info">
                        <div className="chat-avatar">🏷️</div>
                        <div className="chat-header-text">
                            <h2>BharatPrice AI</h2>
                            <span>{content.online}</span>
                        </div>
                    </div>
                    <div className="chat-header-actions">
                        {/* Region indicator */}
                        <button
                            className="region-badge"
                            onClick={() => setShowRegionPicker(true)}
                            title="Change city"
                        >
                            📍 {getCityName(region, language)}{pincode ? ` (${pincode})` : ""}
                        </button>
                        <div className="language-selector">
                            {LANGUAGES.map((lang) => (
                                <button
                                    key={lang.code}
                                    className={`lang-btn ${language === lang.code ? "active" : ""}`}
                                    onClick={() => handleLanguageChange(lang.code)}
                                >
                                    {lang.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Messages */}
                <div className="chat-messages">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`message ${msg.sender}`}>
                            <div className="message-avatar">
                                {msg.sender === "bot" ? "🏷️" : "👤"}
                            </div>
                            <div>
                                <div className="message-bubble">
                                    {formatText(msg.text)}
                                </div>
                                <div className="message-time">{formatTime(msg.timestamp)}</div>
                            </div>
                        </div>
                    ))}

                    {/* Typing Indicator */}
                    {isLoading && (
                        <div className="message bot">
                            <div className="message-avatar">🏷️</div>
                            <div className="message-bubble">
                                <div className="typing-indicator">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Suggestions */}
                {suggestions.length > 0 && !isLoading && (
                    <div className="suggestions">
                        {suggestions.map((s, i) => (
                            <button
                                key={i}
                                className="suggestion-chip"
                                onClick={() => handleSend(s)}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}

                {/* Input Area */}
                <div className="chat-input-area">
                    <div className="chat-input-wrapper">
                        <input
                            ref={inputRef}
                            type="text"
                            className="chat-input"
                            placeholder={content.placeholder}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={isLoading}
                            autoFocus
                        />
                        <button
                            className={`voice-btn ${isRecording ? "recording" : ""}`}
                            onClick={toggleVoice}
                            title={isRecording ? "Stop recording" : "Voice input"}
                        >
                            {isRecording ? "⏹" : "🎙️"}
                        </button>
                        <button
                            className="send-btn"
                            onClick={() => handleSend()}
                            disabled={!input.trim() || isLoading}
                            title="Send message"
                        >
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
