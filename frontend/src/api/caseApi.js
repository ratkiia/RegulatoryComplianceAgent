import axios from "axios";

const API_BASE = "http://localhost:8000";

export const caseApi = {
  async getCases() {
    const res = await axios.get(`${API_BASE}/cases`);
    return res.data;
  },

  async getCase(caseId) {
    const res = await axios.get(`${API_BASE}/cases/${caseId}`);
    return res.data;
  }
};
