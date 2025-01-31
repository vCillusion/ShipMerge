import React, { useState } from "react";
import axios from "axios";

function App() {
  const [invoice, setInvoice] = useState(null);
  const [packingSlip, setPackingSlip] = useState(null);
  const [shippingLabel, setShippingLabel] = useState(null);
  const [mergedPdf, setMergedPdf] = useState(null);

  const handleUpload = async () => {
    if (!invoice || !packingSlip || !shippingLabel) {
      alert("Please upload all three PDFs!");
      return;
    }

    const formData = new FormData();
    formData.append("invoice", invoice);
    formData.append("packing_slip", packingSlip);
    formData.append("shipping_label", shippingLabel);

    const response = await axios.post("https://your-flask-app.onrender.com/upload", formData, {
        responseType: "blob",
      });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    setMergedPdf(url);
  };

  return (
    <div>
      <h2>ShipMerge - Amazon PDF Merger</h2>
      <input type="file" onChange={(e) => setInvoice(e.target.files[0])} />
      <input type="file" onChange={(e) => setPackingSlip(e.target.files[0])} />
      <input type="file" onChange={(e) => setShippingLabel(e.target.files[0])} />
      <button onClick={handleUpload}>Merge PDFs</button>
      {mergedPdf && <a href={mergedPdf} download="merged_shipmerge.pdf">Download Merged PDF</a>}
    </div>
  );
}

export default App;
