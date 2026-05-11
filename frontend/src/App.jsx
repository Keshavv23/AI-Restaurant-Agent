import axios from "axios";
import { useEffect, useRef, useState } from "react";
import { FaRobot } from "react-icons/fa";
import { IoSend } from "react-icons/io5";

function App() {

  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello 👋 Welcome to Spice Garden Restaurant. How can I help you today?"
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // AUTO SCROLL
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages]);

  // SEND MESSAGE
  const sendMessage = async () => {

    if (!input.trim()) return;

    const userMessage = {
      sender: "user",
      text: input
    };

    setMessages((prev) => [...prev, userMessage]);

    const currentInput = input;

    setInput("");

    setLoading(true);

    try {

      const response = await axios.post(
        "http://127.0.0.1:8000/chat",
        {
          message: currentInput
        }
      );

      const aiMessage = {
        sender: "ai",
        text: response.data.reply
      };

      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {

      const errorMessage = {
        sender: "ai",
        text: "Server error 😢"
      };

      setMessages((prev) => [...prev, errorMessage]);

      console.error(error);

    } finally {

      setLoading(false);
    }
  };

  return (

    <div style={styles.container}>

      <div style={styles.chatBox}>

        {/* HEADER */}
        <div style={styles.header}>

          <div style={styles.headerContent}>
            <FaRobot size={24} />
            <h2 style={styles.heading}>
              Spice Garden AI
            </h2>
          </div>

          <p style={styles.subHeading}>
            Smart Restaurant Assistant
          </p>

        </div>

        {/* MESSAGES */}
        <div style={styles.messagesContainer}>

          {messages.map((msg, index) => (

            <div
              key={index}
              style={{
                ...styles.messageWrapper,
                justifyContent:
                  msg.sender === "user"
                    ? "flex-end"
                    : "flex-start"
              }}
            >

              <div
                style={{
                  ...styles.message,

                  backgroundColor:
                    msg.sender === "user"
                      ? "#4f46e5"
                      : "#ffffff",

                  color:
                    msg.sender === "user"
                      ? "white"
                      : "#111827",

                  border:
                    msg.sender === "ai"
                      ? "1px solid #e5e7eb"
                      : "none"
                }}
              >
                {msg.text}
              </div>

            </div>

          ))}

          {/* LOADING */}
          {loading && (

            <div style={styles.loadingContainer}>

              <div style={styles.typingBubble}>
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </div>

            </div>
          )}

          <div ref={messagesEndRef}></div>

        </div>

        {/* INPUT AREA */}
        <div style={styles.inputArea}>

          <input
            type="text"
            placeholder="Type your message..."
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}

            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
          />

          <button
            style={styles.button}
            onClick={sendMessage}
          >
            <IoSend size={20} />
          </button>

        </div>

      </div>

    </div>
  );
}

const styles = {

  container: {
    background:
      "linear-gradient(to right, #0f172a, #111827)",

    height: "100vh",

    display: "flex",

    justifyContent: "center",

    alignItems: "center",

    fontFamily: "Arial"
  },

  chatBox: {

    width: "420px",

    height: "700px",

    backgroundColor: "#f9fafb",

    borderRadius: "25px",

    display: "flex",

    flexDirection: "column",

    overflow: "hidden",

    boxShadow: "0 0 40px rgba(0,0,0,0.4)"
  },

  header: {

    background:
      "linear-gradient(to right, #4f46e5, #7c3aed)",

    padding: "20px",

    color: "white"
  },

  headerContent: {

    display: "flex",

    alignItems: "center",

    gap: "10px"
  },

  heading: {
    margin: 0
  },

  subHeading: {

    marginTop: "5px",

    opacity: 0.9,

    fontSize: "14px"
  },

  messagesContainer: {

    flex: 1,

    padding: "20px",

    overflowY: "auto",

    display: "flex",

    flexDirection: "column",

    gap: "12px"
  },

  messageWrapper: {
    display: "flex"
  },

  message: {

    maxWidth: "75%",

    padding: "14px 18px",

    borderRadius: "18px",

    lineHeight: "1.5",

    fontSize: "15px"
  },

  loadingContainer: {
    display: "flex"
  },

  typingBubble: {

    backgroundColor: "white",

    padding: "12px 16px",

    borderRadius: "16px",

    border: "1px solid #ddd",

    fontSize: "22px",

    display: "flex",

    gap: "4px"
  },

  inputArea: {

    display: "flex",

    padding: "15px",

    backgroundColor: "white",

    borderTop: "1px solid #e5e7eb"
  },

  input: {

    flex: 1,

    padding: "14px",

    borderRadius: "15px",

    border: "1px solid #d1d5db",

    outline: "none",

    fontSize: "15px"
  },

  button: {

    marginLeft: "10px",

    width: "55px",

    border: "none",

    borderRadius: "15px",

    background:
      "linear-gradient(to right, #4f46e5, #7c3aed)",

    color: "white",

    cursor: "pointer",

    display: "flex",

    justifyContent: "center",

    alignItems: "center"
  }
};

export default App;