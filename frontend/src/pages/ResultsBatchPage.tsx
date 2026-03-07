import { useLocation } from "react-router-dom";
import jsPDF from "jspdf";

const classIdToName: Record<string, string> = {
  "0": "Cutter marks and fish marks",
  "1": "Scratches and Black spots",
  "2": "Fingerprints and stains",
  "3": "Ink marks",
  "4": "Jig Marks",
  "5": "Machining Marks",
  "6": "Overcut",
  "7": "Pocket",
};

const ResultsBatchPage = () => {
  const location = useLocation();
  const batchResults = location.state?.batchResults || [];

  const generateBatchReport = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text("Blade Inspection Batch Report", 20, 20);

    let y = 40;

    batchResults.forEach((result: any, index: number) => {
      if (y > 240) {
        doc.addPage();
        y = 20;
      }

      doc.setFontSize(14);
      doc.text(`Image ${index + 1}`, 20, y);
      y += 10;

      // Add image to PDF
      doc.addImage(
        `data:image/png;base64,${result.predicted_image}`,
        "PNG",
        20,
        y,
        80,
        60
      );

      y += 70;

      const counts: Record<string, number> = {};
      result.classes.forEach((cls: number) => {
        counts[cls] = (counts[cls] || 0) + 1;
      });

      doc.setFontSize(12);
      Object.keys(counts).forEach((key) => {
        const label = classIdToName[key];
        doc.text(`${label} - ${counts[key]}`, 20, y);
        y += 8;
      });

      y += 10;
    });

    doc.save("Batch_Blade_Report.pdf");
  };

  return (
    <div className="p-8 flex flex-col gap-12">
      {batchResults.map((result: any, index: number) => (
        <div key={index} className="border p-4 rounded-xl shadow">
          <h2 className="text-xl font-bold mb-4">
            Image {index + 1}
          </h2>

          <img
            src={`data:image/png;base64,${result.predicted_image}`}
            className="w-full mb-4 rounded-xl"
          />
        </div>
      ))}

      <button
        onClick={generateBatchReport}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-bold"
      >
        Generate Batch Report
      </button>
    </div>
  );
};

export default ResultsBatchPage;