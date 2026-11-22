'use client';

import { apiFetch } from "@/lib/api";

import { useEffect, useRef, useState } from "react";
import DatePicker from "react-datepicker";
import { Plus, X, ArrowDownLeft, ArrowUpRight, Landmark, Pencil, Trash2 } from "lucide-react";
import "react-datepicker/dist/react-datepicker.css";

type User = { user_id: number; name: string };
type IncomeSource = { income_source_id: number; name: string; description?: string };
type ExpenseCategory = { expense_category_id: number; name: string; description?: string };
type InvestmentCategory = { id: number; investment_type: string };
type InvestmentSubcategory = { id: number; investment_subcategory_name: string; category_id: number };
type Currency = { currency_id: number; currency_name: string; currency_code: string };
type Region = { region_id: number; region_name: string; currency_id: number };
type Unit = { unit_id: number; unit_name: string };
type LiabilityType = { liability_id: number; liability_type: string };
type LiabilityRecord = {
  id: number;
  liability_id: number;
  liability_type: string;
  value: number;
  currency: string;
  comment: string;
  date: string;
  value_inr: number;
};

const TAB_LABELS: Record<string, string> = {
  income: 'Income',
  expense: 'Expenses',
  investment: 'Investments',
  dividend: 'Dividends',
  instruments: 'Instruments',
  liability: 'Liabilities',
};

export default function TransactionsPage() {
  const [activeTab, setActiveTab] = useState<'income' | 'expense' | 'investment' | 'dividend' | 'instruments' | 'liability'>('income');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [incomeSources, setIncomeSources] = useState<any[]>([]);
  const [expenseCategories, setExpenseCategories] = useState<ExpenseCategory[]>([]);
  const [investmentCategories, setInvestmentCategories] = useState<InvestmentCategory[]>([]);
  const [investmentSubcats, setInvestmentSubcats] = useState<InvestmentSubcategory[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [liabilityTypes, setLiabilityTypes] = useState<LiabilityType[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const formRef = useRef<HTMLDivElement | null>(null);

  // form data for each tab
  const [incomeForm, setIncomeForm] = useState<any>({});
  const [expenseForm, setExpenseForm] = useState<any>({});
  const [investmentForm, setInvestmentForm] = useState<any>({});
  const [dividendForm, setDividendForm] = useState<any>({});
  const [instrumentForm, setInstrumentForm] = useState<any>({});
  const [liabilityForm, setLiabilityForm] = useState<any>({});
  const [newLiabilityType, setNewLiabilityType] = useState("");
  const [editingLiabilityId, setEditingLiabilityId] = useState<number | null>(null);

  // Autocomplete Data
  const [stockSummaries, setStockSummaries] = useState<any[]>([]);
  const [existingInstruments, setExistingInstruments] = useState<any[]>([]);
  
  // Import Modal State
  const [showImportModal, setShowImportModal] = useState(false);
  const [importForm, setImportForm] = useState({
      user_id: "",
      bank_name: "",
      file: null as File | null,
      currency: "INR" 
  });
  const [availableBanks, setAvailableBanks] = useState<string[]>([]);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [mutualFundSummary, setMutualFundSummary] = useState<any[]>([]);

  // Map endpoints for investment types -> endpoint
  const investmentEndpointMap: Record<number, string> = {
    1: "/api/investment/bullion",       // Bullion
    9: "/api/investment/crypto",        // Crypto
    2: "/api/investment/stocks",        // Indian Stock
    3: "/api/investment/real-estate",   // Land
    5: "/api/investment/mutual-fund",   // Mutual Fund
  };

  // load reference data once
  useEffect(() => {
    async function loadRefs() {
      try {
        const [
          usersRes,
          incRes,
          expRes,
          invCatRes,
          invSubRes,
          curRes,
          regRes,
          unitRes,
          liabilityTypesRes
        ] = await Promise.all([
          apiFetch("/api/categories/users").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/income-sources").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/expense-category").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/investment-category").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/investment-subcategory").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/currencies").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/region").then(r => r.json()).catch(() => []),
          apiFetch("/api/categories/units").then(r => r.json()).catch(() => []),
          apiFetch("/api/liabilities/types").then(r => r.json()).catch(() => [])
        ]);

        setUsers(usersRes || []);
        setIncomeSources(incRes || []);
        setExpenseCategories(expRes || []);
        setInvestmentCategories(invCatRes || []);
        setInvestmentSubcats(invSubRes || []);
        setCurrencies(curRes || []);
        setRegions(regRes || []);
        setUnits(unitRes || []);
        setLiabilityTypes(liabilityTypesRes || []);
      } catch (err) {
        console.error("Failed to load reference data", err);
      }
    }
    loadRefs();
  }, []);


// Open the tab requested by a dashboard link, for example ?tab=dividend
useEffect(() => {
  const requested = new URLSearchParams(window.location.search).get("tab");
  const tabs = ["income", "expense", "investment", "dividend", "instruments", "liability"];
  if (requested && tabs.includes(requested)) {
    setActiveTab(requested as typeof activeTab);
    setShowForm(false);
  }
}, []);

// Fetch active tab to do calculations
useEffect(() => {
  setCurrentPage(1);
  fetchRecent();

  if (activeTab === 'investment') {
      apiFetch("/api/summary/mutual-funds")
        .then(res => res.json())
        .then(data => setMutualFundSummary(data))
        .catch(err => console.error("Failed to fetch mutual fund summary", err));
  }
    // Fetch Stock Summaries for Autocomplete
    apiFetch("/api/summary/stocks")
      .then(res => res.json())
      .then(data => setStockSummaries(data))
      .catch(err => console.error("Failed to fetch stock summaries", err));
}, [activeTab]);

async function fetchRecent() {
  try {
    let records: any[] = [];

    if (activeTab === "expense") {
      const res = await apiFetch("/api/expenses");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    } else if (activeTab === "investment") {
      const endpoints = Object.values(investmentEndpointMap);
      const responses = await Promise.allSettled(
        endpoints.map((endpoint) => fetch(endpoint))
      );

      const allData = await Promise.all(
        responses
          .filter((r): r is PromiseFulfilledResult<Response> => r.status === "fulfilled")
          .map((r) => r.value.json())
      );

       records = allData.flatMap((d) => (Array.isArray(d) ? d : d?.results || []));
    } else if (activeTab === "dividend") {
      const res = await apiFetch("/api/dividends");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    } else if (activeTab === "instruments") {
         const res = await apiFetch("/api/protected-instruments");
         const data = await res.json();
         records = Array.isArray(data) ? data : data?.results || [];
         setExistingInstruments(records);
    } else if (activeTab === "liability") {
      const res = await apiFetch("/api/liabilities");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    } else {
      // default = income
      const res = await apiFetch("/api/income");
      const data = await res.json();
      records = Array.isArray(data) ? data : data?.results || [];
    }

    // Sort all tabs by their relevant date field
    const sorted = records.sort((a: any, b: any) => {
      const dateA = new Date(a.earned_date || a.spent_date || a.investment_date || a.date || 0);
      const dateB = new Date(b.earned_date || b.spent_date || b.investment_date || b.date || 0);
      return dateB.getTime() - dateA.getTime(); // latest first
    });
    setRecent(sorted);
  } catch (err) {
    console.error("fetchRecent error", err);
    setRecent([]);
  }
}

  // helper to map id -> display name using loaded refs
  function userName(id?: number) {
    if (!id) return "";
    const u = users.find(x => x.user_id === Number(id));
    return u?.name ?? String(id);
  }
  function incomeSourceName(id?: number) {
    if (!id) return "";
    const s = incomeSources.find(x => x.income_source_id === Number(id));
    return s?.name ?? String(id);
  }
  function expenseCategoryName(id?: number) {
    if (!id) return "";
    const s = expenseCategories.find(x => x.expense_category_id === Number(id));
    return s?.name ?? String(id);
  }
  function investmentTypeName(id?: number) {
    if (!id) return "";
    const s = investmentCategories.find(x => x.id === Number(id));

    return s?.investment_type ?? String(id);
  }
  function invSubName(id?: number) {
    if (!id) return "";
    const s = investmentSubcats.find(x => x.id === Number(id));
    return s?.investment_subcategory_name ?? String(id);
  }



  function currencyCode(id?: number) {
    if (!id) return "";
    const s = currencies.find(x => x.currency_id === Number(id));
    return s?.currency_code ?? String(id);
  }

  // Submit handlers
  async function submitIncome(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const body = {
        user_id: Number(incomeForm.user_id),
        source_id: Number(incomeForm.income_source_id || incomeForm.source_id || incomeForm.source),
        amount: Number(incomeForm.amount),
        currency: incomeForm.currency || (currencies[0]?.currency_code ?? "INR"),
        earned_date: new Date(incomeForm.earned_date).toISOString()
      };
      const res = await apiFetch("/api/income", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`Income POST failed: ${res.status} ${JSON.stringify(body)}`);
      alert("Income saved");
      //setIncomeForm({});
      await fetchRecent();
    } catch (err) {
      console.error(err);
      alert("Failed to save income (see console)");
    } finally {
      setLoading(false);
    }
  }

  async function submitExpense(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const body = {
        user_id: Number(expenseForm.user_id),
        category_id: Number(expenseForm.category_id),
        amount: Number(expenseForm.amount),
        currency: expenseForm.currency || (currencies[0]?.currency_code ?? "INR"),
        spent_date: new Date(expenseForm.spent_date).toISOString()
      };
      const res = await apiFetch("/api/expenses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`Expense POST failed: ${res.status} ${JSON.stringify(body)}`);
      alert("Expense saved");
//       setExpenseForm({});
      await fetchRecent();
    } catch (err) {
      console.error(err);
      alert("Failed to save expense (see console)");
    } finally {
      setLoading(false);
    }
  }

  // Investment submission - choose endpoint based on investment_type_id
  async function submitInvestment(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);

    try {
      const invType = Number(investmentForm.investment_type_id || investmentForm.investment_type);
      const endpoint = investmentEndpointMap[invType] ?? "/api/investment/stocks";

      // Build payload according to your sample structures.
      // We'll try to fill minimal required fields depending on type.
      let payload: any = {
        investor: Number(investmentForm.investor),
        currency_id: Number(investmentForm.currency_id),
        investment_type_id: invType,
        investment_subcategory_id: investmentForm.investment_subcategory_id ? Number(investmentForm.investment_subcategory_id) : null,
        investment_date: investmentForm.investment_date || new Date().toISOString().substring(0, 10),
        transaction_type: investmentForm.transaction_type || "BUY"
      };

      // additional fields based on type
      if (invType === 2) {
        // Indian Stock
        payload = {
          ...payload,
          stock_symbol: investmentForm.stock_symbol || "UNKNOWN",
          stock_name: investmentForm.stock_name || investmentForm.stock_symbol || "Stock",
          initial_price_per_stock: Number(investmentForm.initial_price_per_stock || investmentForm.price || 0),
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          stock_quantity: Number(investmentForm.stock_quantity || 0),
          dividend_paying: investmentForm.dividend_paying || false
        };
      } else if (invType === 5) {
        // Mutual Fund
        payload = {
          ...payload,
          scheme_code: investmentForm.scheme_code || investmentForm.scheme || "",
          fund_name: investmentForm.fund_name || investmentForm.scheme_name || "",
          initial_price_per_unit: investmentForm.initial_price_per_unit || investmentForm.initial_price || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          unit_quantity: Number(investmentForm.unit_quantity || 0),
          total_amount_after_sale: Number(investmentForm.total_amount_after_sale || 0)
        };
      } else if (invType === 1) {
        // Bullion
        payload = {
          ...payload,
          metal_name: investmentForm.metal_name || invSubName(investmentForm.investment_subcategory_id) || "Gold",
          initial_price_per_gram: investmentForm.initial_price_per_gram || investmentForm.initial_price || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          quantity_in_grams: Number(investmentForm.quantity_in_grams || 0)
        };
      } else if (invType === 3) {
        // Land / Real estate
        payload = {
          ...payload,
          property_name: investmentForm.property_name || "Property",
          property_location: investmentForm.property_location || "",
          property_type: investmentForm.property_type || "Plot",
          initial_price_per_sqyds: investmentForm.initial_price_per_sqyds || "0",
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          area_in_sqyds: Number(investmentForm.area_in_sqyds || 0)
        };
      } else if (invType === 9) {
        // Crypto
        payload = {
          ...payload,
          coin_symbol: investmentForm.coin_symbol || investmentForm.stock_symbol || "BTC",
          crypto_name: investmentForm.crypto_name || investmentForm.coin_symbol || "Crypto",
          initial_price_per_coin: Number(investmentForm.initial_price_per_coin || 0),
          total_invested_amount: Number(investmentForm.total_invested_amount || 0),
          coin_quantity: Number(investmentForm.coin_quantity || 0),
          total_amount_after_sale: Number(investmentForm.total_amount_after_sale || 0)
        };
      }

      // POST
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Investment POST failed: ${res.status} ${txt}`);
      }
      alert("Investment saved");
//       setInvestmentForm({});
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to save investment: " + (err?.message || ""));
    } finally {
      setLoading(false);
    }
  }

  // Dividend submission
  async function submitDividend(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        investor: Number(dividendForm.investor),
        region_id: Number(dividendForm.region_id),
        currency_id: Number(dividendForm.currency_id),
        stock_symbol: dividendForm.stock_symbol,
        stock_name: dividendForm.stock_name,
        amount: Number(dividendForm.amount),
        received_date: dividendForm.received_date ? new Date(dividendForm.received_date).toISOString() : new Date().toISOString()
      };

      const res = await apiFetch("/api/dividends", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
         const txt = await res.text().catch(() => "");
         throw new Error(`Dividend POST failed: ${res.status} ${txt}`);
      }
      alert("Dividend saved");
      //setDividendForm({});
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to save dividend: " + err.message);
    } finally {
      setLoading(false);
    }
  }



    // Instrument submission
  async function submitInstrument(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const payload = {
          policy_number: instrumentForm.policy_number,
        user_id: Number(instrumentForm.user_id),
        name: instrumentForm.name,
        provider: instrumentForm.provider,
        category: instrumentForm.category,
        frequency: instrumentForm.frequency, // Optional
        contribution: Number(instrumentForm.contribution),
        start_date: instrumentForm.start_date ? new Date(instrumentForm.start_date).toISOString().substring(0, 10) : new Date().toISOString().substring(0, 10),
        maturity_date: instrumentForm.maturity_date ? new Date(instrumentForm.maturity_date).toISOString().substring(0, 10) : null,
        guaranteed_amount: instrumentForm.guaranteed_amount ? Number(instrumentForm.guaranteed_amount) : null,
        notes: instrumentForm.notes
      };

      const res = await apiFetch("/api/protected-instruments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) {
         const txt = await res.text().catch(() => "");
         throw new Error(`Instrument POST failed: ${res.status} ${txt}`);
      }
      alert("Instrument saved");
      //setInstrumentForm({});
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to save instrument: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function submitLiability(e?: any) {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        liability_id: Number(liabilityForm.liability_id),
        value: Number(liabilityForm.value),
        currency: liabilityForm.currency || (currencies[0]?.currency_code ?? "INR"),
        comment: (liabilityForm.comment || "").trim(),
        date: liabilityForm.date || new Date().toISOString().substring(0, 10),
      };
      if (!payload.liability_id || !payload.value) {
        throw new Error("Choose a liability type and enter an amount");
      }

      const isEditing = editingLiabilityId !== null;
      const res = await fetch(
        isEditing ? `/api/liabilities/${editingLiabilityId}` : "/api/liabilities",
        {
          method: isEditing ? "PUT" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      );
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Liability save failed: ${res.status} ${txt}`);
      }
      alert(isEditing ? "Liability updated." : "Liability saved. The dashboard converts it to INR.");
      setLiabilityForm({});
      setEditingLiabilityId(null);
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to save liability: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  async function addLiabilityType(e?: any) {
    if (e) e.preventDefault();
    const name = newLiabilityType.trim();
    if (!name) return;
    setLoading(true);
    try {
      const res = await apiFetch("/api/liabilities/types", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ liability_type: name })
      });
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error(`Type POST failed: ${res.status} ${txt}`);
      }
      const created: LiabilityType = await res.json();
      const refreshed: LiabilityType[] = await apiFetch("/api/liabilities/types").then(r => r.json()).catch(() => []);
      setLiabilityTypes(refreshed);
      setLiabilityForm((prev: any) => ({ ...prev, liability_id: created.liability_id }));
      setNewLiabilityType("");
    } catch (err: any) {
      console.error(err);
      alert("Failed to add liability type: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function editLiability(item: LiabilityRecord) {
    setEditingLiabilityId(item.id);
    setLiabilityForm({
      liability_id: item.liability_id,
      value: item.value,
      currency: item.currency,
      comment: item.comment || "",
      date: item.date ? new Date(item.date).toISOString().substring(0, 10) : "",
    });
    setShowForm(true);
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function cancelLiabilityEdit() {
    setEditingLiabilityId(null);
    setLiabilityForm({});
  }

  async function deleteLiability(id: number) {
    if (!confirm("Delete this liability entry?")) return;
    setLoading(true);
    try {
      const res = await apiFetch(`/api/liabilities/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
      if (editingLiabilityId === id) cancelLiabilityEdit();
      await fetchRecent();
    } catch (err: any) {
      console.error(err);
      alert("Failed to delete liability: " + err.message);
    } finally {
      setLoading(false);
    }
  }


  // Filtered subcategories when investment type changes
  const filteredInvestmentSubcats = (typeId?: number) =>
    investmentSubcats.filter(s => s.category_id === Number(typeId));

  function formatDate(dateStr: string) {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

function formatAmount(amount: any, currency?: string) {
  if (!amount) return "0";

  const num = Number(amount);
  const symbolMap: Record<string, string> = {
    INR: "₹",
    USD: "$",
    EUR: "€",
    PLN: "zł",
    GBP: "£",
    JPY: "¥"
  };

  // Normalize currency to uppercase in case API sends lowercase
  const currencyKey = (currency || '').toUpperCase();
  const symbol = symbolMap[currencyKey] || '';

  // Format number using locale
  // For crypto (investment_type 9), we want more precision
  const maxDigits = activeTab === 'investment' ? 8 : 2;
  const formatted = num.toLocaleString('en-IN', { maximumFractionDigits: maxDigits });

  return `${symbol}${formatted}`;
}

  // Pagination
  const totalPages = Math.ceil(recent.length / itemsPerPage);
  const paginatedData = recent.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Quick scroll-to-form using floating + button
  function scrollToForm() {
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // small helper to render recent rows replacing ids with names where possible
  function renderRecentCell(key: string, value: any) {
    if (key.toLowerCase().includes("user") || key === "user_id") return userName(value);
    if (key.toLowerCase().includes("source") || key === "source_id" || key === "income_source_id") return incomeSourceName(value);
    if (key.toLowerCase().includes("category") && activeTab === "expense") return expenseCategoryName(value);
    if (key.toLowerCase().includes("investment_type") || key === "investment_type_id") return investmentTypeName(value);
    if (key.toLowerCase().includes("investment_subcategory") || key === "investment_subcategory_id") return invSubName(value);
    if (key.toLowerCase().includes("currency")) return currencyCode(value);
    // else default
    return (value === null || value === undefined) ? "" : String(value);
  }

  return (
    <div className="space-y-6 pb-8">
      <div className="max-w-8xl mx-auto space-y-4">

        {/* Header */}
        <div className="page-head">
          <div>
            <h1 className="page-title">Transactions</h1>
            <p className="page-sub">Track and manage your income, expenses, and investments.</p>
          </div>
          <div className="flex items-center gap-2.5">
            <button
              onClick={() => {
                  setShowImportModal(true);
                  apiFetch("/api/import/banks")
                      .then(r => r.json())
                      .then(data => setAvailableBanks(data))
                      .catch(err => console.error("Failed to fetch banks", err));
              }}
              className="btn btn-secondary"
            >
              Import file
            </button>
            <button
              onClick={() => setShowForm(!showForm)}
              className="btn btn-primary"
            >
              {showForm ? <X size={15} aria-hidden="true" /> : <Plus size={15} aria-hidden="true" />}
              {showForm ? 'Close' : 'New transaction'}
            </button>
          </div>
        </div>

        {/* Tabs - Full Width Segmented Control */}
        <div className="seg" role="tablist" aria-label="Transaction type">
          {(['income', 'expense', 'investment', 'dividend', 'instruments', 'liability'] as const).map(tab => (
            <button
              key={tab}
              role="tab"
              aria-selected={activeTab === tab}
              onClick={() => setActiveTab(tab)}
              className={`seg-item ${
                activeTab === tab ? 'is-active' : ''
              }`}
            >
              {TAB_LABELS[tab]}
            </button>
          ))}
        </div>

        {/* Form - Slide down animation */}
        {showForm && (
            <div ref={formRef} className="card animate-slideDown mb-6">
              <div className="card-head">
                <h2 className="card-title">
                  {activeTab === "liability" && editingLiabilityId !== null ? "Edit Liability" : `Add ${TAB_LABELS[activeTab]}`}
                </h2>
                <span className="card-note">All fields marked by the API contract</span>
              </div>
              <div className="p-5 sm:p-6">

              {/* Income Form */}
              {activeTab === "income" && (
                  <form onSubmit={submitIncome} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select user dropdown */}
                      <div>
                        <select value={incomeForm.user_id ?? ""} onChange={(e) => setIncomeForm({...incomeForm, user_id: e.target.value})} className={selectClass}>
                            <option value="">Select User</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={incomeForm.currency ?? ""} onChange={(e) => setIncomeForm({...incomeForm, currency: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select income source dropdown */}
                      <div>
                        <select value={incomeForm.income_source_id ?? ""} onChange={(e) => setIncomeForm({...incomeForm, income_source_id: e.target.value})} className={selectClass}>
                            <option value="">Select Income Source</option>
                                {incomeSources.map(s => <option key={s.income_source_id} value={s.income_source_id}>{s.name}</option>)}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" value={incomeForm.amount ?? ""} onChange={(e) => setIncomeForm({...incomeForm, amount: e.target.value})} placeholder="Amount" className={inputClass} />
                      </div>

                      {/* Date calendar */}
                      <div>
                          <input type="date"
                            value={incomeForm.earned_date ? new Date(incomeForm.earned_date).toISOString().substring(0, 10) : new Date().toISOString().substring(0, 10)}
                            onChange={(e) =>
                              setIncomeForm({ ...incomeForm, earned_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                      {/* Checkboxes for recurring entries and auto learn */}
                      <div className="flex flex-wrap items-center gap-4 text-[length:var(--text-sm)] font-medium text-[var(--color-ink-2)] md:col-span-full">
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input type="checkbox" checked={!!incomeForm.is_recurring} onChange={(e) => setIncomeForm({...incomeForm, is_recurring: e.target.checked})} className="accent-[var(--color-primary)]" />
                          <span>Recurring</span>
                        </label>
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input type="checkbox" checked={!!incomeForm.auto_learn} onChange={(e) => setIncomeForm({...incomeForm, auto_learn: e.target.checked})} className="accent-[var(--color-primary)]" />
                          <span>Auto-learn</span>
                        </label>
                      </div>

                    </div>

                    {/* save income button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="btn btn-primary">
                        {loading ? "Saving..." : "Save Income"}
                      </button>
                    </div>

                  </form>
              )}

              {/* Expense Form */}
              {activeTab === "expense" && (
                  <form onSubmit={submitExpense} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select user dropdown */}
                      <div>
                        <select value={expenseForm.user_id ?? ""} onChange={(e) => setExpenseForm({...expenseForm, user_id: e.target.value})}   className={selectClass}>
                            <option value="">Select User</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={expenseForm.currency ?? ""} onChange={(e) => setExpenseForm({...expenseForm, currency: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select expense category dropdown */}
                      <div>
                        <select value={expenseForm.category_id ?? ""} onChange={(e) => setExpenseForm({...expenseForm, category_id: e.target.value})} className={selectClass}>
                            <option value="">Select Category</option>
                            {expenseCategories.map(c => <option key={c.expense_category_id} value={c.expense_category_id}>{c.name}</option>)}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" value={expenseForm.amount ?? ""} onChange={(e) => setExpenseForm({...expenseForm, amount: e.target.value})} placeholder="Amount" className={inputClass} />
                      </div>


                      {/* Date calendar */}
                      <div>
                          <input type="date"
                            value={expenseForm.spent_date ?? new Date().toISOString().substring(0, 10)}
                            onChange={(e) =>
                              setExpenseForm({ ...expenseForm, spent_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                      {/* Checkboxes for recurring entries and auto learn */}
                      <div className="flex flex-wrap items-center gap-4 text-[length:var(--text-sm)] font-medium text-[var(--color-ink-2)] md:col-span-full">
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input type="checkbox" checked={!!expenseForm.is_recurring} onChange={(e) => setExpenseForm({...expenseForm, is_recurring: e.target.checked})} className="accent-[var(--color-primary)]" />
                          <span>Recurring</span>
                        </label>
                        <label className="flex items-center gap-1.5 cursor-pointer">
                          <input type="checkbox" checked={!!expenseForm.auto_learn} onChange={(e) => setExpenseForm({...expenseForm, auto_learn: e.target.checked})} className="accent-[var(--color-primary)]" />
                          <span>Auto-learn</span>
                        </label>
                      </div>

                    </div>

                    {/* save expense button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="btn btn-primary">
                        {loading ? "Saving..." : "Save Expense"}
                      </button>
                    </div>

                  </form>
              )}

              {/* Liability Form */}
              {activeTab === "liability" && (
                <form onSubmit={submitLiability} className="space-y-4">
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
                    <div>
                      <label className="field-label" htmlFor="liability-type">Liability type</label>
                      <select
                        id="liability-type"
                        value={liabilityForm.liability_id ?? ""}
                        onChange={(e) => setLiabilityForm({ ...liabilityForm, liability_id: e.target.value })}
                        className={selectClass}
                      >
                        <option value="">Select liability</option>
                        {liabilityTypes.map(t => (
                          <option key={t.liability_id} value={t.liability_id}>{t.liability_type}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="field-label" htmlFor="liability-currency">Currency due</label>
                      <select
                        id="liability-currency"
                        value={liabilityForm.currency ?? ""}
                        onChange={(e) => setLiabilityForm({ ...liabilityForm, currency: e.target.value })}
                        className={selectClass}
                      >
                        <option value="">Currency</option>
                        {currencies.map(c => (
                          <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="field-label" htmlFor="liability-value">Outstanding amount</label>
                      <input
                        id="liability-value"
                        type="number"
                        step="0.01"
                        value={liabilityForm.value ?? ""}
                        onChange={(e) => setLiabilityForm({ ...liabilityForm, value: e.target.value })}
                        placeholder="Amount in the currency due"
                        className={inputClass}
                      />
                    </div>

                    <div>
                      <label className="field-label" htmlFor="liability-comment">Which loan</label>
                      <input
                        id="liability-comment"
                        type="text"
                        value={liabilityForm.comment ?? ""}
                        onChange={(e) => setLiabilityForm({ ...liabilityForm, comment: e.target.value })}
                        placeholder="For example marriage loan"
                        className={inputClass}
                      />
                    </div>

                    <div>
                      <label className="field-label" htmlFor="liability-date">As of date</label>
                      <input
                        id="liability-date"
                        type="date"
                        value={liabilityForm.date || new Date().toISOString().substring(0, 10)}
                        onChange={(e) => setLiabilityForm({ ...liabilityForm, date: e.target.value })}
                        className={`${inputClass} cursor-pointer`}
                      />
                    </div>
                  </div>

                  <div className="flex flex-wrap items-end gap-2 rounded-[var(--radius-panel)] bg-[var(--color-well)] p-3">
                    <div className="min-w-[180px] flex-1">
                      <label className="field-label" htmlFor="new-liability-type">New liability type</label>
                      <input
                        id="new-liability-type"
                        type="text"
                        value={newLiabilityType}
                        onChange={(e) => setNewLiabilityType(e.target.value)}
                        placeholder="For example Car Loan"
                        className={inputClass}
                      />
                    </div>
                    <button type="button" onClick={addLiabilityType} disabled={loading} className="btn btn-secondary">
                      Add type
                    </button>
                  </div>

                  <p className="text-[length:var(--text-xs)] text-[var(--color-muted)]">
                    Use the same “Which loan” text each month. The dashboard takes the newest entry per loan and converts it to INR, so months never add up.
                  </p>

                  <div className="flex justify-end gap-2 pt-2">
                    {editingLiabilityId !== null && (
                      <button type="button" onClick={cancelLiabilityEdit} className="btn btn-secondary">
                        Cancel
                      </button>
                    )}
                    <button type="submit" disabled={loading} className="btn btn-primary">
                      {loading ? "Saving..." : editingLiabilityId !== null ? "Update Liability" : "Save Liability"}
                    </button>
                  </div>
                </form>
              )}

              {/* Investment Form */}
              {activeTab === "investment" && (
                  <form onSubmit={submitInvestment} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">

                      {/* select investor dropdown */}
                      <div>
                        <select value={investmentForm.investor ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investor: e.target.value})} className={selectClass}>
                          <option value="">Select Investor</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={investmentForm.currency_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, currency_id: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_id}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* select investment category dropdown */}
                      <div>
                        <select value={investmentForm.investment_type_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investment_type_id: Number(e.target.value), investment_subcategory_id: undefined})} className={selectClass}>
                            <option value="">Investment Type</option>
                            {investmentCategories.map(ic => <option key={ic.id} value={ic.id}>{ic.investment_type}</option>)}
                        </select>
                      </div>

                      {/* Dependent subcategory dropdown: show only when there are sub categories */}
                      <div>
                        <select value={investmentForm.investment_subcategory_id ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, investment_subcategory_id: e.target.value})} className={selectClass}>
                            <option value="">Subcategory (if applicable)</option>
                                {filteredInvestmentSubcats(investmentForm.investment_type_id).map(s => (
                            <option key={s.id} value={s.id}>{s.investment_subcategory_name}</option>
                            ))}
                        </select>
                      </div>

                      {/* amount text field */}
                      <div>
                        <input type="number" step="0.01" placeholder="Total invested amount" value={investmentForm.total_invested_amount ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, total_invested_amount: e.target.value})} className={inputClass} />
                      </div>

                      {/* Date calendar */}
                      <div>
                          <input type="date"
                            value={investmentForm.investment_date ?? new Date().toISOString().substring(0, 10)}
                            onChange={(e) =>
                              setInvestmentForm({ ...investmentForm, investment_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                      {/* Based on investment type, show type-specific fields */}
                      {/* Type-specific helper fields (stock example) */}
                      {Number(investmentForm.investment_type_id) === 2 && (
                          <>
                           <input list="stock-symbols" placeholder="Stock symbol" value={investmentForm.stock_symbol ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_symbol: e.target.value})} className={inputClass} />
                           <input list="stock-names" placeholder="Stock name" value={investmentForm.stock_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_name: e.target.value})} className={inputClass} />
                           <input type="number" step="0.01" placeholder="Price per stock" value={investmentForm.initial_price_per_stock ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_stock: e.target.value})} className={inputClass} />
                           <input type="number" step="0.0001" placeholder="Quantity" value={investmentForm.stock_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, stock_quantity: e.target.value})} className={inputClass} />
                           {/* Dividend Paying Checkbox */}
                           <div className="flex items-center gap-2 px-1">
                              <input
                                type="checkbox"
                                id="dividend_paying"
                                checked={!!investmentForm.dividend_paying}
                                onChange={(e) => setInvestmentForm({...investmentForm, dividend_paying: e.target.checked})}
                                className="h-4 w-4 accent-[var(--color-primary)]"
                              />
                              <label htmlFor="dividend_paying" className="cursor-pointer text-[length:var(--text-sm)] font-medium text-[var(--color-ink-2)]">
                                Dividend Paying Stock
                              </label>
                           </div>
                          </>
                      )}

                      {/* Mutual Fund fields */}
                      {Number(investmentForm.investment_type_id) === 5 && (
                          <>
                            <input 
                                list="scheme-codes" 
                                placeholder="Scheme code" 
                                value={investmentForm.scheme_code ?? ""} 
                                onChange={(e) => setInvestmentForm({...investmentForm, scheme_code: e.target.value})} 
                                className={inputClass} 
                            />
                            <datalist id="scheme-codes">
                                {mutualFundSummary.map((mf) => (
                                    <option key={`${mf.scheme_code}-${mf.fund_name}`} value={mf.scheme_code}>
                                        {mf.fund_name}
                                    </option>
                                ))}
                            </datalist>

                            <input 
                                list="fund-names" 
                                placeholder="Fund name" 
                                value={investmentForm.fund_name ?? ""} 
                                onChange={(e) => {
                                    const selectedName = e.target.value;
                                    const match = mutualFundSummary.find(mf => mf.fund_name === selectedName);
                                    setInvestmentForm({
                                        ...investmentForm, 
                                        fund_name: selectedName,
                                        scheme_code: match ? match.scheme_code : investmentForm.scheme_code
                                    });
                                }} 
                                className={inputClass} 
                            />
                            <datalist id="fund-names">
                                {mutualFundSummary.map((mf) => (
                                    <option key={`${mf.scheme_code}-${mf.fund_name}-name`} value={mf.fund_name} />
                                ))}
                            </datalist>

                            <input type="number" step="0.0001" placeholder="Unit quantity" value={investmentForm.unit_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, unit_quantity: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Price per unit" value={investmentForm.initial_price_per_unit ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_unit: e.target.value})} className={inputClass} />
                          </>
                      )}

                      {/* Bullion fields */}
                      {Number(investmentForm.investment_type_id) === 1 && (
                          <>
                            <input placeholder="Metal name (Gold/Silver)" value={investmentForm.metal_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, metal_name: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Price per gram" value={investmentForm.initial_price_per_gram ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_gram: e.target.value})} className={inputClass} />
                            <input type="number" placeholder="Quantity (grams)" value={investmentForm.quantity_in_grams ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, quantity_in_grams: e.target.value})} className={inputClass} />
                          </>
                      )}

                      {/* Crypto fields */}
                      {Number(investmentForm.investment_type_id) === 9 && (
                        <>
                          <input placeholder="Coin symbol" value={investmentForm.coin_symbol ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, coin_symbol: e.target.value})} className={inputClass} />
                          <input placeholder="Crypto name" value={investmentForm.crypto_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, crypto_name: e.target.value})} className={inputClass} />
                          <input type="number" step="0.00000001" placeholder="Price per coin" value={investmentForm.initial_price_per_coin ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_coin: e.target.value})} className={inputClass} />
                          <input type="number" step="0.00000001" placeholder="Quantity" value={investmentForm.coin_quantity ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, coin_quantity: e.target.value})} className={inputClass} />
                        </>
                      )}

                      {/* Real Estate fields */}
                      {Number(investmentForm.investment_type_id) === 3 && (
                        <>
                          <input placeholder="Property Name" value={investmentForm.property_name ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, property_name: e.target.value})} className={inputClass} />
                          <input placeholder="Property Type (Plot/Apt/House)" value={investmentForm.property_type ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, property_type: e.target.value})} className={inputClass} />
                          <input placeholder="Location" value={investmentForm.property_location ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, property_location: e.target.value})} className={inputClass} />
                          <div className="grid grid-cols-2 gap-2">
                             <input type="number" step="0.01" placeholder="Area (Sq.Yds)" value={investmentForm.area_in_sqyds ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, area_in_sqyds: e.target.value})} className={inputClass} />
                             <input type="number" step="0.01" placeholder="Price per Sq.Yd" value={investmentForm.initial_price_per_sqyds ?? ""} onChange={(e) => setInvestmentForm({...investmentForm, initial_price_per_sqyds: e.target.value})} className={inputClass} />
                          </div>
                        </>
                      )}

                    </div>

                    {/* save investment button */}
                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="btn btn-primary">
                        {loading ? "Saving..." : "Save Investment"}
                      </button>
                    </div>

                  </form>
              )}

              {/* Dividend Form */}
              {activeTab === "dividend" && (
                  <form onSubmit={submitDividend} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                      {/* select investor dropdown */}
                      <div>
                        <select value={dividendForm.investor ?? ""} onChange={(e) => setDividendForm({...dividendForm, investor: e.target.value})} className={selectClass}>
                          <option value="">Select Investor</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                      {/* select region dropdown */}
                      <div>
                        <select value={dividendForm.region_id ?? ""} onChange={(e) => setDividendForm({...dividendForm, region_id: e.target.value})} className={selectClass}>
                            <option value="">Select Region</option>
                            {regions.map((r: any) => <option key={r.region_id} value={r.region_id}>{r.region_name}</option>)}
                        </select>
                      </div>

                      {/* select currency dropdown */}
                      <div>
                        <select value={dividendForm.currency_id ?? ""} onChange={(e) => setDividendForm({...dividendForm, currency_id: e.target.value})} className={selectClass}>
                            <option value="">Currency</option>
                            {currencies.map(c => <option key={c.currency_id} value={c.currency_id}>{c.currency_name} ({c.currency_code})</option>)}
                        </select>
                      </div>

                      {/* Stock Symbol with Autocomplete */}
                      <div>
                        <input list="stock-symbols" placeholder="Stock Symbol" value={dividendForm.stock_symbol ?? ""} onChange={(e) => setDividendForm({...dividendForm, stock_symbol: e.target.value})} className={inputClass} />
                        <datalist id="stock-symbols">
                            {stockSummaries.map((s, i) => <option key={i} value={s.stock_symbol} />)}
                        </datalist>
                      </div>

                      {/* Stock Name with Autocomplete */}
                      <div>
                        <input list="stock-names" placeholder="Stock Name" value={dividendForm.stock_name ?? ""} onChange={(e) => setDividendForm({...dividendForm, stock_name: e.target.value})} className={inputClass} />
                         <datalist id="stock-names">
                            {stockSummaries.map((s, i) => <option key={i} value={s.stock_name} />)}
                        </datalist>
                      </div>

                      {/* Amount */}
                      <div>
                        <input type="number" step="0.01" placeholder="Amount" value={dividendForm.amount ?? ""} onChange={(e) => setDividendForm({...dividendForm, amount: e.target.value})} className={inputClass} />
                      </div>

                      {/* Date */}
                      <div>
                          <input type="date"
                            value={dividendForm.received_date ?? new Date().toISOString().substring(0, 10)}
                            onChange={(e) =>
                              setDividendForm({ ...dividendForm, received_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                    </div>

                    <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="btn btn-primary">
                        {loading ? "Saving..." : "Save Dividend"}
                      </button>
                    </div>
                  </form>
              )}

            {/* Instruments Form */}
              {activeTab === "instruments" && (
                  <form onSubmit={submitInstrument} className="space-y-4">
                     <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

                       {/* User */}
                       <div>
                        <select value={instrumentForm.user_id ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, user_id: e.target.value})} className={selectClass}>
                          <option value="">Select User</option>
                            {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                        </select>
                      </div>

                       {/* Name with Autocomplete */}
                       <div>
                         <input list="instrument-names" placeholder="Instrument Name (e.g. LIC)" value={instrumentForm.name ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, name: e.target.value})} className={inputClass} />
                         <datalist id="instrument-names">
                             {Array.from(new Set(existingInstruments.map(i => i.name))).map((n: any, idx) => <option key={idx} value={n} />)}
                         </datalist>
                       </div>

                       {/* Provider with Autocomplete */}
                       <div>
                         <input list="instrument-providers" placeholder="Provider (e.g. HDFC)" value={instrumentForm.provider ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, provider: e.target.value})} className={inputClass} />
                         <datalist id="instrument-providers">
                             {Array.from(new Set(existingInstruments.map(i => i.provider))).map((p: any, idx) => <option key={idx} value={p} />)}
                         </datalist>
                       </div>

                        {/* Category */}
                      <div>
                        <select value={instrumentForm.category ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, category: e.target.value})} className={selectClass}>
                            <option value="">Category</option>
                            <option value="insurance">Insurance</option>
                            <option value="savings">Savings</option>
                            <option value="pension">Pension</option>
                            <option value="other">Other</option>
                        </select>
                      </div>

                        {/* Policy Number with Autocomplete */}
                       <div>
                         <input list="instrument-policy-number" placeholder="Instrument policy number (e.g. AXA12345)" value={instrumentForm.policy_number ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, policy_number: e.target.value})} className={inputClass} />
                         <datalist id="instrument-policy-number">
                             {Array.from(new Set(existingInstruments.map(i => i.policy_number))).map((n: any, idx) => <option key={idx} value={n} />)}
                         </datalist>
                       </div>

                      {/* Frequency */}
                      <div>
                          <select value={instrumentForm.frequency ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, frequency: e.target.value})} className={selectClass}>
                              <option value="">Frequency</option>
                              <option value="Monthly">Monthly</option>
                              <option value="Quarterly">Quarterly</option>
                              <option value="Half Yearly">Half Yearly</option>
                              <option value="Yearly">Yearly</option>
                              <option value="One Time">One Time</option>
                          </select>
                      </div>

                       {/* Contribution */}
                      <div>
                        <input type="number" placeholder="Contribution Amount" value={instrumentForm.contribution ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, contribution: e.target.value})} className={inputClass} />
                      </div>

                      {/* Guaranteed Amount */}
                      <div>
                        <input type="number" placeholder="Guaranteed Amt (Optional)" value={instrumentForm.guaranteed_amount ?? ""} onChange={(e) => setInstrumentForm({...instrumentForm, guaranteed_amount: e.target.value})} className={inputClass} />
                      </div>

                      {/* Notes - Spanning row 2 and 3 in the last column */}
                      <div className="md:col-start-4 md:row-start-2 md:row-span-2">
                        <textarea 
                          placeholder="Notes" 
                          value={instrumentForm.notes ?? ""} 
                          onChange={(e) => setInstrumentForm({...instrumentForm, notes: e.target.value})} 
                          className={`${inputClass} h-full min-h-[100px] resize-none`}
                        />
                      </div>

                       {/* Start Date */}
                      <div className="md:col-start-2 md:row-start-3">
                          <label className="field-label mb-1.5">Start date</label>
                          <input type="date"
                            value={instrumentForm.start_date ?? new Date().toISOString().substring(0, 10)}
                            onChange={(e) =>
                              setInstrumentForm({ ...instrumentForm, start_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                       {/* Maturity Date */}
                      <div>
                          <label className="field-label mb-1.5">Maturity date</label>
                          <input type="date"
                            value={instrumentForm.maturity_date ?? ""}
                            onChange={(e) =>
                              setInstrumentForm({ ...instrumentForm, maturity_date: e.target.value })
                            }
                            className={`${inputClass} cursor-pointer`}
                          />
                      </div>

                     </div>
                     <div className="flex justify-end pt-2">
                      <button type="submit" disabled={loading} className="btn btn-primary">
                        {loading ? "Saving..." : "Save Instrument"}
                      </button>
                    </div>
                  </form>
              )}
              </div>
            </div>
        )}

        {/* Recent transactions */}
        <section className="card overflow-hidden">
          <div className="card-head">
            <div>
              <h2 className="card-title">Recent {TAB_LABELS[activeTab]}</h2>
              <p className="card-note">Newest entries from the ledger</p>
            </div>
            <span className="badge badge-neutral">{recent.length} records</span>
          </div>

          <div>
            {paginatedData.length === 0 && (
              <div className="empty-state">
                <p className="state-title">Nothing recorded yet</p>
                <p className="text-[length:var(--text-sm)]">New {activeTab} entries appear here as they are added.</p>
              </div>
            )}

            {paginatedData.map((item: any, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between gap-3 border-b border-[var(--color-rule)] px-5 py-3.5 transition-colors last:border-b-0 hover:bg-[var(--color-well)]"
              >
                <div className="flex min-w-0 items-center gap-3">
                  <span
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-[8px] border ${
                      activeTab === 'income'
                        ? 'border-[color-mix(in_oklab,var(--color-success)_30%,transparent)] bg-[color-mix(in_oklab,var(--color-success)_12%,transparent)] text-[var(--color-success-text)]'
                        : activeTab === 'expense'
                          ? 'border-[color-mix(in_oklab,var(--color-danger)_28%,transparent)] bg-[color-mix(in_oklab,var(--color-danger)_10%,transparent)] text-[var(--color-danger-text)]'
                          : 'border-[var(--color-rule)] bg-[var(--color-well)] text-[var(--color-accent)]'
                    }`}
                    aria-hidden="true"
                  >
                    {activeTab === 'income' ? <ArrowDownLeft size={16} /> : activeTab === 'expense' ? <ArrowUpRight size={16} /> : <Landmark size={16} />}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-[length:var(--text-sm)] font-semibold text-[var(--color-ink)]">
                      {activeTab === 'income'
                        ? incomeSourceName(item.source_id)
                        : activeTab === 'expense'
                          ? expenseCategoryName(item.category_id)
                          : activeTab === 'liability'
                            ? item.liability_type
                            : `${investmentTypeName(item.investment_type_id)} : ${invSubName(item.investment_subcategory_id) || (item.stock_symbol || item.fund_name || item.metal_name || 'Investment')}`
                      }
                    </p>
                    <p className="mt-0.5 flex items-center gap-2 text-[length:var(--text-xs)] text-[var(--color-muted)]">
                      <span className="truncate">
                        {activeTab === 'liability'
                          ? `${item.comment ? `${item.comment} · ` : ''}INR equivalent ${formatAmount(item.value_inr || 0, 'INR')}`
                          : userName(item.user_id || item.investor)}
                      </span>
                      <span className="h-3 w-px shrink-0 bg-[var(--color-rule)]" aria-hidden="true" />
                      <span className="shrink-0 tabular-nums">{formatDate(item.earned_date || item.spent_date || item.investment_date || item.date)}</span>
                    </p>
                  </div>
                </div>

                <div className="flex shrink-0 flex-col items-end gap-1.5">
                  <p className={`text-[length:var(--text-md)] font-semibold tabular-nums ${
                    activeTab === 'income' ? 'text-[var(--color-success-text)]' :
                    activeTab === 'expense' ? 'text-[var(--color-danger-text)]' : 'text-[var(--color-ink)]'
                  }`}>
                    {formatAmount(
                      activeTab === 'liability'
                        ? item.value || 0
                        : activeTab === 'investment'
                        ? item.total_invested_amount || 0
                        : activeTab === 'income'
                          ? item.amount || 0
                          : item.amount,
                      item.currency_id ? currencyCode(item.currency_id) : item.currency || ''
                    )}
                  </p>
                  {activeTab === 'liability' && (
                    <div className="flex items-center gap-1.5">
                      <button
                        type="button"
                        onClick={() => editLiability(item as LiabilityRecord)}
                        className="btn btn-secondary btn-sm"
                      >
                        <Pencil size={12} aria-hidden="true" />
                        Edit
                      </button>
                      <button
                        type="button"
                        onClick={() => deleteLiability(item.id)}
                        className="btn btn-danger btn-sm btn-icon"
                        aria-label="Delete liability entry"
                      >
                        <Trash2 size={12} aria-hidden="true" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-[var(--color-rule)] bg-[var(--color-well)] px-5 py-3 text-[length:var(--text-xs)]">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="btn btn-secondary btn-sm"
              >
                Previous
              </button>
              <span className="font-medium tabular-nums text-[var(--color-ink-2)]">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="btn btn-secondary btn-sm"
              >
                Next
              </button>
            </div>
          )}
            </section>

            <style jsx>{`
        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideDown {
          animation: slideDown 0.3s ease-out;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-slideDown { animation: none; }
        }
      `}</style>

      </div>

      {/* Floating control scrolls to the form */}
      <button
        onClick={scrollToForm}
        className="btn btn-primary btn-icon fixed bottom-8 right-8 h-12 w-12 rounded-full border-[color-mix(in_oklab,var(--color-accent)_55%,transparent)] shadow-[var(--shadow-pop)]"
        title="New transaction"
        aria-label="New transaction"
      >
        <Plus size={20} aria-hidden="true" />
      </button>

      {/* Import Modal */}
      {showImportModal && (
          <div className="fixed inset-0 z-[400] flex items-start justify-center overflow-y-auto bg-[color-mix(in_oklab,var(--color-ink)_55%,transparent)] p-4 backdrop-blur-[2px] sm:items-center">
              <div className="card relative my-8 w-full max-w-4xl p-6 sm:p-8">
                  <button
                      onClick={() => {
                          setShowImportModal(false);
                          setPreviewData([]); // Reset preview on close
                      }}
                      className="btn btn-ghost btn-icon btn-sm absolute right-4 top-4"
                      aria-label="Close import dialog"
                  >
                      <X size={16} aria-hidden="true" />
                  </button>
                  <h2 className="page-title mb-6 pr-10 text-[length:var(--text-2xl)]">
                      {previewData.length > 0 ? "Review and confirm import" : "Import transactions"}
                  </h2>

                  {!previewData.length ? (
                      // STEP 1: UPLOAD FORM
                      <div className="space-y-4 max-w-lg mx-auto">
                          {/* User Select */}
                          <div>
                              <label className="field-label">User</label>
                              <select
                                  value={importForm.user_id}
                                  onChange={(e) => setImportForm({...importForm, user_id: e.target.value})}
                                  className={selectClass}
                              >
                                  <option value="">Select User</option>
                                  {users.map(u => <option key={u.user_id} value={u.user_id}>{u.name}</option>)}
                              </select>
                          </div>

                          {/* Bank Select */}
                          <div>
                              <label className="field-label">Bank</label>
                              <select
                                  value={importForm.bank_name}
                                  onChange={(e) => setImportForm({...importForm, bank_name: e.target.value})}
                                  className={selectClass}
                              >
                                  <option value="">Select Bank</option>
                                  {availableBanks.map(bank => (
                                      <option key={bank} value={bank}>{bank.toUpperCase()}</option>
                                  ))}
                              </select>
                          </div>

                           {/* Currency Select */}
                           <div>
                              <label className="field-label">Currency</label>
                              <select
                                  value={importForm.currency}
                                  onChange={(e) => setImportForm({...importForm, currency: e.target.value})}
                                  className={selectClass}
                              >
                                  {currencies.map(c => <option key={c.currency_id} value={c.currency_code}>{c.currency_name} ({c.currency_code})</option>)}
                              </select>
                          </div>

                          {/* File Upload */}
                           <div>
                              <label className="field-label">CSV or TXT file</label>
                              <input
                                  type="file"
                                  accept=".csv,.txt"
                                  onChange={(e) => setImportForm({...importForm, file: e.target.files?.[0] || null})}
                                  className="field py-2"
                              />
                          </div>

                          {/* Preview Button */}
                          <div className="pt-4 flex justify-end">
                              <button
                                  onClick={async () => {
                                      if (!importForm.user_id || !importForm.bank_name || !importForm.file) {
                                          alert("Please fill all fields");
                                          return;
                                      }

                                      const formData = new FormData();
                                      formData.append("bank_name", importForm.bank_name);
                                      formData.append("currency", importForm.currency);
                                      formData.append("file", importForm.file);

                                      try {
                                          const res = await apiFetch("/api/import/preview", {
                                              method: "POST",
                                              body: formData
                                          });
                                          const data = await res.json();
                                          if(!res.ok) throw new Error(data.detail || "Preview failed");

                                          setPreviewData(data); // Move to Step 2

                                      } catch (err: any) {
                                          alert("Error: " + err.message);
                                      }
                                  }}
                                  className="btn btn-primary w-full"
                              >
                                  Preview Transactions
                              </button>
                          </div>
                      </div>
                  ) : (
                      // STEP 2: PREVIEW TABLE
                      <div className="space-y-4">
                          <div className="max-h-[60vh] overflow-x-auto rounded-[var(--radius-panel)] border border-[var(--color-edge)]">
                              <table className="w-full text-xs sm:text-sm text-left">
                                  <thead className="sticky top-0 z-10 bg-[var(--color-well)] text-[length:var(--text-xs)] font-semibold text-[var(--color-muted)]">
                                      <tr>
                                          <th className="px-4 py-3">Date</th>
                                          <th className="px-4 py-3">Description</th>
                                          <th className="px-4 py-3 text-right">Amount</th>
                                          <th className="px-4 py-3">Type</th>
                                          <th className="px-4 py-3 w-1/4">Category / Source</th>
                                          <th className="px-4 py-3 text-center">Action</th>
                                      </tr>
                                  </thead>
                                  <tbody className="font-medium">
                                      {previewData.map((txn, idx) => (
                                          <tr key={idx} className={`border-b border-[var(--color-rule)] last:border-b-0 hover:bg-[var(--color-well)] ${txn.ignore ? 'opacity-45' : ''}`}>
                                              <td className="whitespace-nowrap px-4 py-2.5 tabular-nums text-[var(--color-ink-2)]">{txn.date}</td>
                                              <td className="max-w-xs truncate px-4 py-2.5 text-[var(--color-ink)]" title={txn.description}>{txn.description}</td>
                                              <td className={`px-4 py-2.5 text-right font-semibold tabular-nums ${txn.type === 'income' ? 'text-[var(--color-success-text)]' : 'text-[var(--color-danger-text)]'}`}>
                                                  {txn.amount} {txn.currency}
                                              </td>
                                              <td className="px-4 py-2.5 capitalize text-[var(--color-ink-2)]">{txn.type}</td>
                                              <td className="px-4 py-2.5">
                                                  {txn.type === 'income' ? (
                                                      <select
                                                          value={txn.source_id || ""}
                                                          disabled={txn.ignore}
                                                          onChange={(e) => {
                                                              const newVal = Number(e.target.value);
                                                              const newData = [...previewData];
                                                              newData[idx].source_id = newVal;
                                                              newData[idx].learn_keyword = txn.description;
                                                              setPreviewData(newData);
                                                          }}
                                                          className="field field-sm"
                                                      >
                                                          {incomeSources.map(s => <option key={s.income_source_id} value={s.income_source_id}>{s.name}</option>)}
                                                      </select>
                                                  ) : (
                                                      <select
                                                          value={txn.category_id || ""}
                                                          disabled={txn.ignore}
                                                          onChange={(e) => {
                                                              const newVal = Number(e.target.value);
                                                              const newData = [...previewData];
                                                              newData[idx].category_id = newVal;
                                                              newData[idx].learn_keyword = txn.description;
                                                              setPreviewData(newData);
                                                          }}
                                                          className="field field-sm"
                                                      >
                                                          {expenseCategories.map(c => <option key={c.expense_category_id} value={c.expense_category_id}>{c.name}</option>)}
                                                      </select>
                                                  )}
                                              </td>
                                              <td className="px-4 py-2.5 text-center">
                                                  <button
                                                      title={txn.ignore ? "Include this transaction" : "Ignore this transaction"}
                                                      onClick={() => {
                                                          const newData = [...previewData];
                                                          newData[idx].ignore = !newData[idx].ignore;
                                                          setPreviewData(newData);
                                                      }}
                                                      className={`btn btn-sm ${txn.ignore ? 'btn-secondary' : 'btn-danger'}`}
                                                  >
                                                      {txn.ignore ? "Include" : "Ignore"}
                                                  </button>
                                              </td>
                                          </tr>
                                      ))}
                                  </tbody>
                              </table>
                          </div>

                          <div className="flex items-center justify-between gap-3 border-t border-[var(--color-rule)] pt-4">
                              <button
                                  onClick={() => setPreviewData([])} // Back to upload
                                  className="btn btn-secondary btn-sm"
                              >
                                  &larr; Back
                              </button>

                              <button
                                  onClick={async () => {
                                      setLoading(true);
                                      try {
                                          const finalTransactions = previewData.filter(t => !t.ignore);
                                          if (finalTransactions.length === 0) {
                                              alert("No transactions to import!");
                                              setLoading(false);
                                              return;
                                          }

                                          const payload = {
                                              user_id: Number(importForm.user_id),
                                              transactions: finalTransactions
                                          };

                                          const res = await apiFetch("/api/import/confirm", {
                                              method: "POST",
                                              headers: { "Content-Type": "application/json" },
                                              body: JSON.stringify(payload)
                                          });

                                          const data = await res.json();
                                          if(!res.ok) throw new Error(data.detail || "Confirm failed");

                                          alert(`Successfully imported ${data.processed} transactions!`);
                                          if (data.learned > 0) {
                                              alert(`Learned ${data.learned} new categorization rules.`);
                                          }

                                          setShowImportModal(false);
                                          setPreviewData([]);
                                          fetchRecent();
                                      } catch (err: any) {
                                          alert("Error: " + err.message);
                                      } finally {
                                          setLoading(false);
                                      }
                                  }}
                                  disabled={loading}
                                  className="btn btn-primary"
                              >
                                  {loading ? "Importing..." : `Confirm & Import (${previewData.filter(t => !t.ignore).length})`}
                              </button>
                          </div>
                      </div>
                  )}
              </div>
          </div>
      )}
    </div>
  );
}

const inputClass = 'field';
const selectClass = 'field';