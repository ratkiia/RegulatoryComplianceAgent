import axios from "axios";

const API_BASE = "http://localhost:8000";

export const hitlApi = {
  async approve(caseId) {
    const res = await axios.post(`${API_BASE}/hitl/approve`, { case_id: caseId });
    return res.data;
  },

  async reject(caseId, comment) {
    const res = await axios.post(`${API_BASE}/hitl/reject`, {
      case_id: caseId,
      comment
    });
    return res.data;
  },

  async override(caseId, overrideData) {
    const res = await axios.post(`${API_BASE}/hitl/override`, {
      case_id: caseId,
      override_violations: overrideData.override_violations,
      override_score: overrideData.override_score,
      override_final_response: overrideData.override_final_response,
      comment: overrideData.comment
    });
    return res.data;
  }
};
