import React, { useState } from "react";
import axios from "axios";
import { Button, Card, CardContent, Typography, CircularProgress, FormControlLabel, Checkbox, TextField } from "@mui/material";

function App() {
  const [invoice, setInvoice] = useState(null);
  const [packingSlip, setPackingSlip] = useState(null);
  const [shippingLabel, setShippingLabel] = useState(null);
  const [mergedPdf, setMergedPdf] = useState(null);
  const [previewPdf, setPreviewPdf] = useState(null);
  const [loading, setLoading] = useState(false);
  const [rotateLabel, setRotateLabel] = useState(false);
  const [trimPercentage, setTrimPercentage] = useState(100);

  const handleUpload = async () => {
    if (!invoice || !packingSlip || !shippingLabel) {
      alert("Please upload all three PDFs!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("invoice", invoice);
    formData.append("packing_slip", packingSlip);
    formData.append("shipping_label", shippingLabel);
    formData.append("rotate_label", rotateLabel ? "landscape" : "portrait");
    formData.append("trim_percentage", trimPercentage);

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";
    try {
      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        headers: { Accept: "application/pdf" },
        responseType: "blob",
      });
      const pdfBlob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(pdfBlob);
      setMergedPdf(url);
    } catch (error) {
      console.error("Error merging PDFs", error);
      alert("Failed to merge PDFs. Please try again.");
    }
    setLoading(false);
  };

  const handlePreview = async () => {
    if (!invoice || !packingSlip || !shippingLabel) {
      alert("Please upload all three PDFs!");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("invoice", invoice);
    formData.append("packing_slip", packingSlip);
    formData.append("shipping_label", shippingLabel);
    formData.append("rotate_label", rotateLabel ? "landscape" : "portrait");
    formData.append("trim_percentage", trimPercentage);

    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:5000";
    try {
      const response = await axios.post(`${BACKEND_URL}/preview`, formData, {
        headers: { Accept: "application/pdf" },
        responseType: "blob",
      });
      const pdfBlob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(pdfBlob);
      setPreviewPdf(url);
    } catch (error) {
      console.error("Error previewing PDFs", error);
      alert("Failed to generate preview. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div style={{ textAlign: "center", padding: "20px", maxWidth: "600px", margin: "auto" }}>
      <Typography variant="h4" gutterBottom>
        ShipMerge - Amazon PDF Merger
      </Typography>
      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Invoice</Typography>
          <input 
            type="file" 
            accept="application/pdf"  // 🔥 Restrict to PDFs only
            onChange={(e) => {
              const file = e.target.files[0];
              if (file && file.type !== "application/pdf") {
                alert("Only PDF files are allowed!");
                return;
              }
              setInvoice(file);
            }} 
          />
        </CardContent>
      </Card>

      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Packing Slip</Typography>
          <input 
            type="file" 
            accept="application/pdf"  // 🔥 Restrict to PDFs only
            onChange={(e) => {
              const file = e.target.files[0];
              if (file && file.type !== "application/pdf") {
                alert("Only PDF files are allowed!");
                return;
              }
              setPackingSlip(file);
            }} 
          />
        </CardContent>
      </Card>

      <Card variant="outlined" style={{ padding: "20px", marginBottom: "20px" }}>
        <CardContent>
          <Typography variant="h6">Upload Shipping Label</Typography>
          <input 
            type="file" 
            accept="application/pdf"  // 🔥 Restrict to PDFs only
            onChange={(e) => {
              const file = e.target.files[0];
              if (file && file.type !== "application/pdf") {
                alert("Only PDF files are allowed!");
                return;
              }
              setShippingLabel(file);
            }} 
          />
        </CardContent>
      </Card>

      <FormControlLabel
        control={<Checkbox checked={rotateLabel} onChange={(e) => setRotateLabel(e.target.checked)} />}
        label="Rotate Shipping Label to Landscape"
      />
      <br />
      <TextField
        label="Trim Shipping Label (%)"
        type="number"
        value={trimPercentage}
        onChange={(e) => setTrimPercentage(e.target.value)}
        inputProps={{ min: 10, max: 100 }}
        style={{ marginTop: "10px", width: "100%" }}
      />
      <br />
      <Button 
        variant="contained" 
        color="primary" 
        onClick={handlePreview} 
        disabled={loading} 
        style={{ marginTop: "20px", marginRight: "10px" }}
      >
        {loading ? <CircularProgress size={24} /> : "Preview PDF"}
      </Button>
      <Button 
        variant="contained" 
        color="secondary" 
        onClick={handleUpload} 
        disabled={loading} 
        style={{ marginTop: "20px" }}
      >
        {loading ? <CircularProgress size={24} /> : "Merge PDFs"}
      </Button>

      {previewPdf && (
        <div style={{ marginTop: "20px" }}>
          <Typography variant="h6">PDF Preview:</Typography>
          <embed 
              src={previewPdf} 
              type="application/pdf" 
              width="100%" 
              height="500px" 
          />
        </div>
      )}

      {mergedPdf && (
        <div style={{ marginTop: "20px" }}>
          <Typography variant="h6">Download Merged PDF:</Typography>
          <a href={mergedPdf} download="merged_shipmerge.pdf">
            <Button variant="contained" color="secondary" style={{ marginTop: "10px" }}>
              Download PDF
            </Button>
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
