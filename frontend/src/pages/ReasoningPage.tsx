import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Collapse,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import SportsCricketIcon from "@mui/icons-material/SportsCricket";
import client from "../../api/client";
import logo from "../assets/cricketsense-logo.png";

const ReasoningPage: React.FC = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [reasoning, setReasoning] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showReasoning, setShowReasoning] = useState(false);

  const askQuestion = async () => {
    setError("");
    setAnswer("");
    setReasoning("");
    setShowReasoning(false);

    if (!question.trim()) {
      setError("Please type a question.");
      return;
    }

    setLoading(true);
    try {
      const res = await client.get("/reason", { params: { question } });
      console.log("API response:", res.data);

      const fullResponse =
        res?.data?.final_answer ??
        res?.data?.finalAnswer ??
        res?.data?.answer ??
        "";

      if (!fullResponse) {
        setAnswer("❌ No answer found.");
      } else {
        const finalLineMatch = fullResponse.match(/Final Answer:\s*(.*)/i);
        const concise = finalLineMatch
          ? finalLineMatch[1].trim()
          : fullResponse;

        setAnswer(concise);
        setReasoning(fullResponse);
      }
    } catch (err) {
      console.error("Request error:", err);
      setError("❌ Error fetching answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-start",
        py: 10,
        px: 2,
        backgroundImage: `url("/src/assets/main.jpg")`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundColor: "#0d1117",
        color: "#fff",
        overflowX: "hidden",
      }}
    >
      {/* Cinematic overlay */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          background: "rgba(0, 0, 0, 0.75)",
          backdropFilter: "blur(6px)",
          zIndex: 0,
        }}
      />

      {/* Logo + App Name */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          gap: 1.5,
          mb: 6,
          zIndex: 5,
        }}
      >
        <img
          src={logo}
          alt="CricketSense Logo"
          style={{
            width: 80,
            height: 80,
            borderRadius: "50%",
            border: "2px solid #42a5f5",
            boxShadow: "0 0 25px rgba(33,150,243,0.8)",
          }}
        />
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: "#fff",
            textShadow: "0 0 15px rgba(33,150,243,0.7)",
          }}
        >
          CricketSense
        </Typography>
      </Box>

      {/* Main Q&A Card */}
      <Paper
        elevation={12}
        sx={{
          position: "relative",
          zIndex: 5,
          width: "95%",
          maxWidth: 750,
          padding: 5,
          borderRadius: 5,
          background: "rgba(255, 255, 255, 0.08)",
          backdropFilter: "blur(20px)",
          boxShadow: "0 8px 60px rgba(0,0,0,0.7)",
          textAlign: "center",
          animation: "fadeIn 1s ease-out",
          "@keyframes fadeIn": {
            from: { opacity: 0, transform: "translateY(30px)" },
            to: { opacity: 1, transform: "translateY(0)" },
          },
        }}
      >
        <Typography
          variant="h5"
          sx={{
            mb: 3,
            fontWeight: 600,
            color: "#90caf9",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 1,
          }}
        >
          <SportsCricketIcon sx={{ fontSize: 28 }} /> Ask a Cricket Question
        </Typography>

        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your cricket question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          InputProps={{
            sx: {
              backgroundColor: "rgba(255,255,255,0.15)",
              borderRadius: 2,
              color: "#fff",
              "& .MuiOutlinedInput-notchedOutline": {
                borderColor: "rgba(255,255,255,0.3)",
              },
              "&:hover .MuiOutlinedInput-notchedOutline": {
                borderColor: "#42a5f5",
              },
            },
          }}
        />

        <Button
          variant="contained"
          onClick={askQuestion}
          fullWidth
          sx={{
            mt: 3,
            height: 50,
            fontSize: "1.05rem",
            fontWeight: 700,
            borderRadius: 2.5,
            background: "linear-gradient(90deg, #1565c0, #42a5f5)",
            boxShadow: "0 0 25px rgba(66,165,245,0.5)",
            "&:hover": {
              background: "linear-gradient(90deg, #0d47a1, #2196f3)",
              boxShadow: "0 0 35px rgba(33,150,243,0.8)",
            },
          }}
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : "ASK"}
        </Button>

        {error && (
          <Typography color="error" sx={{ mt: 2, fontWeight: 500 }}>
            {error}
          </Typography>
        )}

        {/* Answer Section */}
        {answer && (
          <Box
            sx={{
              mt: 4,
              p: 3,
              borderRadius: 3,
              backgroundColor: "rgba(255,255,255,0.1)",
              color: "#b3e5fc",
              boxShadow: "inset 0 0 20px rgba(255,255,255,0.1)",
              textAlign: "left",
              maxHeight: "65vh",
              overflowY: "auto",
            }}
          >
            <Typography
              variant="h6"
              sx={{
                mb: 1.5,
                fontWeight: 700,
                color: "#81d4fa",
                textShadow: "0 0 10px rgba(129,212,250,0.5)",
              }}
            >
              🏏 {answer}
            </Typography>

            {reasoning && (
              <Box sx={{ mt: 2 }}>
                <Button
                  onClick={() => setShowReasoning(!showReasoning)}
                  sx={{
                    color: "#90caf9",
                    textTransform: "none",
                    fontWeight: 500,
                    "&:hover": { color: "#fff" },
                  }}
                  startIcon={
                    showReasoning ? <ExpandLessIcon /> : <ExpandMoreIcon />
                  }
                >
                  {showReasoning ? "Hide reasoning" : "Show reasoning"}
                </Button>
                <Collapse in={showReasoning}>
                  <Typography
                    sx={{
                      mt: 1.5,
                      whiteSpace: "pre-line",
                      fontSize: "0.95rem",
                      color: "#e3f2fd",
                      opacity: 0.9,
                    }}
                  >
                    {reasoning}
                  </Typography>
                </Collapse>
              </Box>
            )}
          </Box>
        )}
      </Paper>

      {/* Footer */}
      <Typography
        variant="body2"
        sx={{
          mt: 6,
          mb: 2,
          color: "#aaa",
          zIndex: 5,
        }}
      >
        © {new Date().getFullYear()} CricketSense — AI-powered cricket insights
      </Typography>
    </Box>
  );
};

export default ReasoningPage;
