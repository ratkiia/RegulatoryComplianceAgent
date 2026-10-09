import React, { useState } from "react";
import { hitlApi } from "../../api/hitlApi";

export function HITLDecisionPanel({ caseId, onUpdate }) {
  const [overrideData, setOverrideData] = useState({
    override_violations: [],
    override_score: "",
    override_final_response: "",
    comment: ""
  });

  const approve = async () => {
    const res = await hitlApi.approve(caseId);
    onUpdate && onUpdate(res);
  };

  const reject = async () => {
    const res = await hitlApi.reject(caseId, overrideData.comment);
    onUpdate && onUpdate(res);
  };

  const override = async () => {
    const res = await hitlApi.override(caseId, overrideData);
    onUpdate && onUpdate(res);
  };

  return (
    <div>
      <h2>HITL Decision</h2>
      <button onClick={approve}>Approve</button>
      <button onClick={reject}>Reject</button>

      <h3>Override</h3>
      <textarea
        placeholder="Override violations JSON"
        onChange={e =>
          setOverrideData({
            ...overrideData,
            override_violations: JSON.parse(e.target.value || "[]")
          })
        }
      />
      <input
        type="number"
        placeholder="Override score"
        value={overrideData.override_score}
        onChange={e =>
          setOverrideData({
            ...overrideData,
            override_score: Number(e.target.value)
          })
        }
      />
      <textarea
        placeholder="Final response"
        value={overrideData.override_final_response}
        onChange={e =>
          setOverrideData({
            ...overrideData,
            override_final_response: e.target.value
          })
        }
      />
      <textarea
        placeholder="Comment"
        value={overrideData.comment}
        onChange={e =>
          setOverrideData({
            ...overrideData,
            comment: e.target.value
          })
        }
      />
      <button onClick={override}>Submit Override</button>
    </div>
  );
}
