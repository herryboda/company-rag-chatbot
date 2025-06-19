import { useState, useEffect } from "react";
import { 
  Activity, 
  TrendingUp, 
  MessageSquare, 
  Star, 
  AlertTriangle,
  RefreshCw,
  Download,
  Settings
} from "lucide-react";

export default function AdminDashboard() {
  const [health, setHealth] = useState(null);
  const [trainingReport, setTrainingReport] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchHealth();
    fetchTrainingReport();
    fetchSuggestions();
  }, []);

  async function fetchHealth() {
    try {
      const res = await fetch("http://localhost:8000/health");
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      console.error("Health fetch error:", err);
    }
  }

  async function fetchTrainingReport() {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/training/report");
      const data = await res.json();
      setTrainingReport(data.report);
    } catch (err) {
      console.error("Training report fetch error:", err);
    } finally {
      setLoading(false);
    }
  }

  async function fetchSuggestions() {
    try {
      const res = await fetch("http://localhost:8000/training/suggestions");
      const data = await res.json();
      setSuggestions(data.suggestions);
    } catch (err) {
      console.error("Suggestions fetch error:", err);
    }
  }

  function getPriorityColor(priority) {
    switch (priority) {
      case "high": return "text-red-600 bg-red-50";
      case "medium": return "text-yellow-600 bg-yellow-50";
      case "low": return "text-green-600 bg-green-50";
      default: return "text-gray-600 bg-gray-50";
    }
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600">Monitor and manage your enhanced RAG chatbot</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg">
        {[
          { id: "overview", label: "Overview", icon: Activity },
          { id: "training", label: "Training", icon: TrendingUp },
          { id: "suggestions", label: "Suggestions", icon: AlertTriangle },
          { id: "settings", label: "Settings", icon: Settings }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
              activeTab === tab.id
                ? "bg-white text-blue-600 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          {/* Health Status */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">System Status</p>
                  <p className={`text-2xl font-bold ${
                    health?.status === "healthy" ? "text-green-600" : "text-red-600"
                  }`}>
                    {health?.status || "Unknown"}
                  </p>
                </div>
                <Activity size={24} className="text-gray-400" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Self Training</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {health?.metrics?.self_training_enabled ? "Enabled" : "Disabled"}
                  </p>
                </div>
                <TrendingUp size={24} className="text-gray-400" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Feedback Collection</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {health?.metrics?.feedback_collection_enabled ? "Active" : "Inactive"}
                  </p>
                </div>
                <MessageSquare size={24} className="text-gray-400" />
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          {trainingReport && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">
                    {trainingReport.data_summary?.training_data_count || 0}
                  </p>
                  <p className="text-sm text-gray-600">Conversations</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {trainingReport.data_summary?.feedback_data_count || 0}
                  </p>
                  <p className="text-sm text-gray-600">Feedback Items</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">
                    {trainingReport.conversation_analysis?.question_types?.policy || 0}
                  </p>
                  <p className="text-sm text-gray-600">Policy Questions</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {Math.round((trainingReport.conversation_analysis?.answer_quality?.specificity_ratio || 0) * 100)}%
                  </p>
                  <p className="text-sm text-gray-600">Answer Quality</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Training Tab */}
      {activeTab === "training" && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Training Report</h3>
            <button
              onClick={fetchTrainingReport}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="text-center py-8">
              <RefreshCw size={32} className="animate-spin mx-auto text-gray-400" />
              <p className="text-gray-600 mt-2">Generating training report...</p>
            </div>
          ) : trainingReport ? (
            <div className="space-y-6">
              {/* Question Types Analysis */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h4 className="text-lg font-semibold mb-4">Question Types</h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(trainingReport.conversation_analysis?.question_types || {}).map(([type, count]) => (
                    <div key={type} className="text-center">
                      <p className="text-2xl font-bold text-blue-600">{count}</p>
                      <p className="text-sm text-gray-600 capitalize">{type}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Answer Quality */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h4 className="text-lg font-semibold mb-4">Answer Quality Metrics</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {trainingReport.conversation_analysis?.answer_quality?.specific_answers || 0}
                    </p>
                    <p className="text-sm text-gray-600">Specific Answers</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {trainingReport.conversation_analysis?.answer_quality?.generic_answers || 0}
                    </p>
                    <p className="text-sm text-gray-600">Generic Answers</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {Math.round(trainingReport.conversation_analysis?.answer_quality?.average_length || 0)}
                    </p>
                    <p className="text-sm text-gray-600">Avg Length</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {Math.round((trainingReport.conversation_analysis?.answer_quality?.specificity_ratio || 0) * 100)}%
                    </p>
                    <p className="text-sm text-gray-600">Quality Score</p>
                  </div>
                </div>
              </div>

              {/* Training Examples */}
              {trainingReport.training_examples && trainingReport.training_examples.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow">
                  <h4 className="text-lg font-semibold mb-4">High-Quality Training Examples</h4>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {trainingReport.training_examples.slice(0, 5).map((example, idx) => (
                      <div key={idx} className="border-l-4 border-green-500 pl-4">
                        <p className="font-medium text-sm">Q: {example.question}</p>
                        <p className="text-sm text-gray-600 mt-1">A: {example.answer.substring(0, 100)}...</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              No training data available
            </div>
          )}
        </div>
      )}

      {/* Suggestions Tab */}
      {activeTab === "suggestions" && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold">Improvement Suggestions</h3>
          
          {suggestions.length > 0 ? (
            <div className="space-y-4">
              {suggestions.map((suggestion, idx) => (
                <div key={idx} className="bg-white p-6 rounded-lg shadow border-l-4 border-yellow-500">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(suggestion.priority)}`}>
                          {suggestion.priority.toUpperCase()}
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {suggestion.type.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{suggestion.message}</p>
                      {suggestion.metric && (
                        <p className="text-sm text-gray-600">Metric: {suggestion.metric}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-600">
              No improvement suggestions available
            </div>
          )}
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold">System Configuration</h3>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold mb-4">Current Settings</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-600">Self Training</p>
                <p className="text-lg font-semibold">
                  {health?.metrics?.self_training_enabled ? "Enabled" : "Disabled"}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Feedback Collection</p>
                <p className="text-lg font-semibold">
                  {health?.metrics?.feedback_collection_enabled ? "Enabled" : "Disabled"}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Quality Threshold</p>
                <p className="text-lg font-semibold">
                  {Math.round((health?.metrics?.quality_threshold || 0) * 100)}%
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Last Updated</p>
                <p className="text-lg font-semibold">
                  {health?.metrics?.timestamp ? formatDate(health.metrics.timestamp) : "Unknown"}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h4 className="text-lg font-semibold mb-4">Export Data</h4>
            <div className="flex gap-4">
              <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                <Download size={16} />
                Export Training Report
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                <Download size={16} />
                Export Feedback Data
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 