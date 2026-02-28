document.addEventListener('alpine:init', () => {
  Alpine.data('app', () => ({
    // --- الحالة الأساسية والمسار ---
    token: localStorage.getItem('gacms_token') || '',
    route: '/',
    routeReady: false,
    loginForm: { email: '', password: '' },
    loginError: '',
    loginLoading: false,
    apiBase: (() => {
      const u = new URL(location.href);
      return u.origin + '/api/v1';
    })(),

    groups: { items: [], total: 0 },
    companies: { items: [], total: 0 },
    companiesAll: { items: [] },
    branches: { items: [], total: 0 },
    branchesForSelect: { items: [] },
    employees: { items: [], total: 0 },
    assets: { items: [], total: 0 },
    alerts: { needing_maintenance: [], warranty_expiring_this_month: [], lost: [] },
    logs: { items: [], total: 0 },
    dashboard: {},

    companiesGroupId: '',
    branchesCompanyId: '',
    employeesCompanyId: '',
    employeesBranchId: '',
    assetsCompanyId: '',
    assetsBranchId: '',
    alertsCompanyId: '',

    groupModalOpen: false,
    editingGroup: null,
    groupForm: { name: '' },
    companyModalOpen: false,
    editingCompany: null,
    companyForm: { name: '', logo_url: '', primary_color: '', legal_text: '', address: '', phone: '', email: '', website: '' },
    branchModalOpen: false,
    editingBranch: null,
    branchForm: { name: '', address: '' },
    employeeModalOpen: false,
    editingEmployee: null,
    employeeForm: { name: '', national_id: '', job_title: '', department: '', status: 'active' },
    assetModalOpen: false,
    editingAsset: null,
    assetForm: { type: 'laptop', brand: '', model: '', serial_number: '', status: 'active', specifications: {}, notes: '' },
    assignModalOpen: false,
    transferModalOpen: false,
    assignEmployeeId: '',
    transferEmployeeId: '',
    transferNotes: '',
    transferCreateHandover: true,
    employeesForAssign: [],

    darkMode: localStorage.getItem('gacms_dark') === 'true',
    searchQuery: '',
    searchResults: null,
    toastMessage: '',
    toastType: 'success',
    lastErrorMsg: '',
    loadingGroups: false,
    loadingAssets: false,
    loadingAssetDetail: false,
    loadingCompanies: false,
    loadingBranches: false,
    loadingEmployees: false,
    loadingDocuments: false,
    loadingAudits: false,
    loadingLogs: false,
    loadingUsers: false,
    savingGroup: false,
    savingCompany: false,
    savingBranch: false,
    savingEmployee: false,
    savingAsset: false,
    savingUser: false,
    savingHandover: false,
    savingAudit: false,
    viewAssetId: null,
    assetDetail: null,
    assetTimeline: [],
    assetMaintenanceRecords: [],
    assetQrUrl: null,

    auditsList: [],
    auditsCompanyId: '',
    auditModalOpen: false,
    newAuditCompanyId: '',
    newAuditBranchId: '',
    branchesForAudit: [],
    scanModalOpen: false,
    scanAuditId: null,
    scanAssetIdInput: '',

    documentsAssetId: '',
    documentsList: [],
    handoverAssetId: '',
    handoverEmployeeId: '',
    documentsAssetsList: [],
    documentsEmployeesList: [],
    documentsCompanyId: '',

    reportsCompanyId: '',
    maintenanceCompanyId: '',
    maintenanceAssets: { items: [] },
    loadingMaintenance: false,
    settingsAssetSpecJson: '',
    loadingDashboard: false,
    loadingAlerts: false,
    searchLoading: false,
    loadingDocumentsData: false,
    exportingBackup: false,
    restoringBackup: false,
    savingSettingsAlerts: false,
    savingSettingsSpecs: false,
    assigning: false,
    transferring: false,
    scanning: false,
    exportingCsv: false,
    downloadingDocumentId: null,
    downloadingAuditId: null,

    usersList: { items: [], total: 0 },
    usersCompanyId: '',
    userModalOpen: false,
    editingUser: null,
    userForm: { email: '', password: '', company_id: '', role: 'company_admin' },

    includeDeletedGroups: false,
    includeDeletedCompanies: false,
    includeDeletedBranches: false,
    includeDeletedEmployees: false,
    includeDeletedAssets: false,
    includeDeletedUsers: false,

    ASSET_SPEC_FIELDS: {
      laptop: [{ key: 'ram', label: 'الرام' }, { key: 'hard_drive', label: 'الهارد' }, { key: 'hard_drive_type', label: 'نوع الهارد' }, { key: 'size', label: 'الحجم' }, { key: 'color', label: 'اللون' }, { key: 'processor', label: 'المعالج' }, { key: 'graphics_card', label: 'كارت الشاشة' }],
      printer: [{ key: 'printer_type', label: 'نوع الطابعة' }, { key: 'connectivity', label: 'التوصيل' }, { key: 'paper_size', label: 'حجم الورق' }, { key: 'color', label: 'اللون' }],
      mobile: [{ key: 'ram', label: 'الرام' }, { key: 'storage', label: 'التخزين' }, { key: 'color', label: 'اللون' }],
      tablet: [{ key: 'ram', label: 'الرام' }, { key: 'storage', label: 'التخزين' }, { key: 'size', label: 'الحجم' }, { key: 'color', label: 'اللون' }],
      desktop: [{ key: 'ram', label: 'الرام' }, { key: 'hard_drive', label: 'الهارد' }, { key: 'processor', label: 'المعالج' }, { key: 'graphics_card', label: 'كارت الشاشة' }],
      monitor: [{ key: 'size', label: 'الحجم' }, { key: 'resolution', label: 'الدقة' }, { key: 'panel_type', label: 'نوع الشاشة' }],
      peripheral: [{ key: 'details', label: 'تفاصيل' }],
      other: [{ key: 'details', label: 'تفاصيل' }]
    },
    alertLabels: { maintenance: 'تحتاج صيانة', warranty: 'الضمان ينتهي هذا الشهر', loss: 'مفقود' },

    toggleDark() {
      this.darkMode = !this.darkMode;
      localStorage.setItem('gacms_dark', this.darkMode);
    },
    showToast(msg, type = 'success') {
      this.toastMessage = msg;
      this.toastType = type;
      const duration = type === 'error' ? 5500 : 3500;
      setTimeout(() => { this.toastMessage = ''; }, duration);
    },
    /** إغلاق كل النوافذ المنبثقة قبل فتح واحدة (يضمن ظهور النافذة المطلوبة فقط) */
    closeAllModals() {
      this.groupModalOpen = false;
      this.userModalOpen = false;
      this.companyModalOpen = false;
      this.branchModalOpen = false;
      this.employeeModalOpen = false;
      this.assetModalOpen = false;
      this.assignModalOpen = false;
      this.transferModalOpen = false;
      this.auditModalOpen = false;
    },
    /** تنقل: يحدّث route فقط (بدون تغيير الـ URL) */
    navigateTo(path) {
      const p = path && path.indexOf('/') === 0 ? path : '/' + (path || '');
      this.route = p;
    },
    actionLabel(action) {
      const labels = { created: 'إنشاء', assigned: 'تعيين', transferred: 'نقل', returned: 'إرجاع', maintenance_start: 'إرسال للصيانة', maintenance_end: 'استلام من الصيانة', lost: 'تسجيل مفقود', retired: 'إستبعاد', updated: 'تحديث', soft_deleted: 'حذف' };
      return labels[action] || action;
    },
    timelineLogText(log) {
      const label = this.actionLabel(log.action_type);
      const fromName = log.from_employee_name;
      const toName = log.to_employee_name;
      if (log.action_type === 'transferred' && (fromName || toName)) {
        const part = [fromName ? 'من ' + fromName : '', toName ? 'إلى ' + toName : ''].filter(Boolean).join(' ');
        return part ? label + ': ' + part : label;
      }
      if ((log.action_type === 'assigned' || log.action_type === 'returned') && (fromName || toName)) {
        const parts = [];
        if (fromName) parts.push('كان مع ' + fromName);
        if (toName) parts.push('صار مع ' + toName);
        return parts.length ? label + ' (' + parts.join(' → ') + ')' : label;
      }
      return label;
    },
    get pageTitle() {
      const t = {
        '/': 'لوحة التحكم',
        '/groups': 'المجموعات',
        '/companies': 'الشركات',
        '/branches': 'الفروع',
        '/employees': 'الموظفون',
        '/assets': 'الأصول',
        '/documents': 'المستندات',
        '/audits': 'التدقيق',
        '/alerts': 'التنبيهات',
        '/maintenance': 'الصيانات',
        '/logs': 'سجل النشاط',
        '/reports': 'التقارير',
        '/settings': 'الإعدادات',
        '/users': 'المستخدمون'
      };
      return t[this.route] || 'GACMS';
    },
    get pageSubtitle() {
      const s = {
        '/': 'نظرة عامة على النظام',
        '/groups': 'إدارة المجموعات',
        '/companies': 'إدارة الشركات',
        '/branches': 'إدارة الفروع',
        '/employees': 'إدارة الموظفين',
        '/assets': 'إدارة الأصول والمعدات',
        '/documents': 'مستندات التسليم والاستلام',
        '/audits': 'جلسات التدقيق والتقارير',
        '/alerts': 'تنبيهات الصيانة والضمان والمفقود',
        '/maintenance': 'أصول قيد الصيانة وربط بالتنبيهات',
        '/logs': 'سجل إجراءات المستخدمين',
        '/reports': 'تصدير تقارير المجموعات والشركات والأصول وغيرها',
        '/settings': 'النسخ الاحتياطي والاستعادة والمظهر',
        '/users': 'إنشاء مستخدمين بصلاحيات لكل شركة'
      };
      return s[this.route] || '';
    },
    async getFetchErrorMsg(r) {
      if (r.ok) return '';
      const text = await r.text();
      try {
        const j = JSON.parse(text);
        const d = j.detail;
        if (typeof d === 'string') return d;
        if (d && d.message) return d.message;
        if (Array.isArray(d) && d[0] && d[0].msg) return d[0].msg;
      } catch (_) {}
      return '';
    },

    async request(method, path, body = null) {
      const opts = {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...(this.token ? { 'Authorization': 'Bearer ' + this.token } : {})
        }
      };
      if (body && (method === 'POST' || method === 'PATCH' || method === 'PUT')) opts.body = JSON.stringify(body);
      this.lastErrorMsg = '';
      try {
        const r = await fetch(this.apiBase + path, opts);
        if (r.status === 401) {
          this.token = '';
          localStorage.removeItem('gacms_token');
          this.showToast('انتهت الجلسة، يرجى تسجيل الدخول مرة أخرى', 'error');
          setTimeout(() => window.location.reload(), 800);
          return null;
        }
        const text = await r.text();
        if (!r.ok) {
          try {
            const j = JSON.parse(text);
            const d = j.detail;
            if (typeof d === 'string') this.lastErrorMsg = d;
            else if (d && d.message) this.lastErrorMsg = d.message;
            else if (Array.isArray(d) && d[0] && d[0].msg) this.lastErrorMsg = d[0].msg;
          } catch (_) {}
        }
        if (!text) return r.ok ? {} : null;
        try { return JSON.parse(text); } catch { return text; }
      } catch (err) {
        this.lastErrorMsg = err && err.message ? err.message : 'خطأ في الاتصال بالسيرفر';
        this.showToast('خطأ في الاتصال. تحقق من الشبكة والسيرفر.', 'error');
        return null;
      }
    },

    async login() {
      this.loginError = '';
      this.loginLoading = true;
      try {
        const res = await fetch(this.apiBase + '/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.loginForm)
        });
        const text = await res.text();
        let data = {};
        try { data = text ? JSON.parse(text) : {}; } catch (_) {}
        const token = data && data.access_token;
        if (res.ok && token) {
          this.token = token;
          localStorage.setItem('gacms_token', token);
          window.location.reload();
          return;
        }
        if (res.status === 429) {
          this.loginError = 'محاولات تسجيل دخول كثيرة. انتظر دقيقة وحاول مرة أخرى.';
        } else {
          const d = data.detail;
          this.loginError = Array.isArray(d) ? (d[0]?.msg || (d[0]?.loc && d[0].loc.join(' ')) || 'فشل تسجيل الدخول') : (typeof d === 'string' ? d : (d && d.message) || (d && d.msg) || 'فشل تسجيل الدخول. تحقق من البريد وكلمة المرور.');
        }
      } catch (e) {
        this.loginError = 'خطأ في الاتصال بالسيرفر. تحقق من تشغيل التطبيق والعنوان (مثلاً http://localhost:8000).';
      }
      this.loginLoading = false;
    },
    logout() {
      this.token = '';
      localStorage.removeItem('gacms_token');
      window.location.reload();
    },

    async doSearch() {
      if (!this.searchQuery || this.searchQuery.length < 2) { this.searchResults = null; return; }
      this.searchLoading = true;
      try {
        const q = encodeURIComponent(this.searchQuery);
        const res = await this.request('GET', '/search?q=' + q + '&limit=10');
        if (res) this.searchResults = res;
      } finally {
        this.searchLoading = false;
      }
    },
    goToAsset(id) {
      this.viewAssetId = id;
      this.searchResults = null;
      this.searchQuery = '';
      this.navigateTo('/assets');
      this.loadAssetDetail(id);
    },
    goToEmployee(id) {
      this.searchResults = null;
      this.searchQuery = '';
      this.employeesCompanyId = '';
      this.employeesBranchId = '';
      this.navigateTo('/employees');
      this.loadGroups();
      this.loadCompaniesAll();
    },
    async loadGroups() {
      this.loadingGroups = true;
      try {
        const inc = this.includeDeletedGroups ? '&include_deleted=true' : '';
        const res = await this.request('GET', '/groups?page=1&page_size=100' + inc);
        this.groups = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingGroups = false;
      }
    },
    async restoreGroup(id) {
      const res = await this.request('POST', '/groups/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadGroups(); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadCompanies() {
      if (!this.companiesGroupId) { this.companies = { items: [], total: 0 }; return; }
      this.loadingCompanies = true;
      try {
        const inc = this.includeDeletedCompanies ? '&include_deleted=true' : '';
        const res = await this.request('GET', '/companies?group_id=' + this.companiesGroupId + '&page=1&page_size=100' + inc);
        this.companies = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingCompanies = false;
      }
    },
    async restoreCompany(id) {
      const res = await this.request('POST', '/companies/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadCompanies(); this.loadCompaniesAll(); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadCompaniesAll() {
      this.companiesAll = { items: [] };
      // محاولة 1: طلب كل الشركات دفعة واحدة (يتطلب backend محدث)
      const first = await this.request('GET', '/companies?page=1&page_size=100');
      if (first && first.items && first.items.length > 0) {
        let all = first.items.slice();
        let page = 2;
        const total = first.total || 0;
        while (all.length < total) {
          const next = await this.request('GET', '/companies?page=' + page + '&page_size=100');
          if (!next || !next.items) break;
          all = all.concat(next.items);
          if (next.items.length === 0) break;
          page++;
        }
        this.companiesAll = { items: all };
        return;
      }
      // محاولة 2: إذا لم يرجع شيء، جلب المجموعات ثم شركات كل مجموعة (يعمل مع أي backend)
      const g = await this.request('GET', '/groups?page=1&page_size=500');
      if (!g || !g.items || g.items.length === 0) return;
      const all = [];
      for (const grp of g.items) {
        const c = await this.request('GET', '/companies?group_id=' + grp.id + '&page=1&page_size=500');
        if (c && c.items) all.push(...c.items);
      }
      this.companiesAll = { items: all };
    },
    async loadBranches() {
      if (!this.branchesCompanyId) { this.branches = { items: [], total: 0 }; return; }
      this.loadingBranches = true;
      try {
        const inc = this.includeDeletedBranches ? '&include_deleted=true' : '';
        const res = await this.request('GET', '/branches?company_id=' + this.branchesCompanyId + '&page=1&page_size=100' + inc);
        this.branches = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingBranches = false;
      }
    },
    async restoreBranch(id) {
      const res = await this.request('POST', '/branches/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadBranches(); this.loadBranchesForEmployees(); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadBranchesForEmployees() {
      if (!this.employeesCompanyId) { this.branchesForSelect = { items: [] }; return; }
      const res = await this.request('GET', '/branches?company_id=' + this.employeesCompanyId + '&page=1&page_size=100');
      this.branchesForSelect = (res && res.items) ? res : { items: [] };
    },
    async loadEmployees() {
      if (!this.employeesCompanyId) { this.employees = { items: [], total: 0 }; return; }
      this.loadingEmployees = true;
      try {
        let path = '/employees?company_id=' + this.employeesCompanyId + '&page=1&page_size=100';
        if (this.employeesBranchId) path += '&branch_id=' + this.employeesBranchId;
        if (this.includeDeletedEmployees) path += '&include_deleted=true';
        const res = await this.request('GET', path);
        this.employees = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingEmployees = false;
      }
    },
    async restoreEmployee(id) {
      const res = await this.request('POST', '/employees/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadEmployees(); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadAssets() {
      if (!this.assetsCompanyId) { this.assets = { items: [], total: 0 }; return; }
      this.loadingAssets = true;
      try {
        let path = '/assets?company_id=' + this.assetsCompanyId + '&page=1&page_size=100';
        if (this.assetsBranchId) path += '&branch_id=' + this.assetsBranchId;
        if (this.includeDeletedAssets) path += '&include_deleted=true';
        const res = await this.request('GET', path);
        this.assets = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingAssets = false;
      }
    },
    async deleteAsset(id) {
      if (!confirm('هل أنت متأكد من حذف هذا الأصل؟')) return;
      const res = await this.request('DELETE', '/assets/' + id);
      if (res != null) { this.showToast('تم الحذف'); this.loadAssets(); if (this.viewAssetId === id) { this.viewAssetId = null; this.assetDetail = null; } } else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },
    async restoreAsset(id) {
      const res = await this.request('POST', '/assets/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadAssets(); if (this.viewAssetId === id) this.loadAssetDetail(id); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadAssetDetail(id) {
      this.loadingAssetDetail = true;
      this.assetDetail = null;
      this.assetTimeline = [];
      this.assetMaintenanceRecords = [];
      if (this.assetQrUrl) { URL.revokeObjectURL(this.assetQrUrl); this.assetQrUrl = null; }
      try {
        const [asset, timeline, maintenance] = await Promise.all([
          this.request('GET', '/assets/' + id),
          this.request('GET', '/assets/' + id + '/timeline'),
          this.request('GET', '/assets/' + id + '/maintenance-records')
        ]);
        if (asset) this.assetDetail = asset;
        if (timeline && Array.isArray(timeline)) this.assetTimeline = timeline;
        if (maintenance && Array.isArray(maintenance)) this.assetMaintenanceRecords = maintenance;
        if (this.assetDetail && this.assetDetail.company_id) {
          const empRes = await this.request('GET', '/employees?company_id=' + this.assetDetail.company_id + '&page=1&page_size=200&status=active');
          this.employeesForAssign = (empRes && empRes.items) ? empRes.items : [];
        }
        if (this.assetDetail && this.token) {
          try {
            const r = await fetch(this.apiBase + '/assets/' + id + '/qr', { headers: { 'Authorization': 'Bearer ' + this.token } });
            if (r.ok) { const blob = await r.blob(); this.assetQrUrl = URL.createObjectURL(blob); }
          } catch (_) {}
        }
      } finally {
        this.loadingAssetDetail = false;
      }
    },
    openAssignModal() {
      this.closeAllModals();
      this.assignEmployeeId = '';
      this.assignModalOpen = true;
    },
    openTransferModal() {
      this.closeAllModals();
      this.transferEmployeeId = '';
      this.transferNotes = '';
      this.transferCreateHandover = true;
      this.transferModalOpen = true;
    },
    async doAssign() {
      if (!this.assignEmployeeId) { this.showToast('يرجى اختيار الموظف', 'error'); return; }
      this.assigning = true;
      try {
        const res = await this.request('POST', '/assets/' + this.viewAssetId + '/assign', { employee_id: this.assignEmployeeId });
        if (res) { this.assignModalOpen = false; this.showToast('تم التعيين بنجاح'); this.loadAssetDetail(this.viewAssetId); }
        else this.showToast(this.lastErrorMsg || 'فشل التعيين', 'error');
      } finally {
        this.assigning = false;
      }
    },
    async doTransfer() {
      if (!this.transferEmployeeId) { this.showToast('يرجى اختيار الموظف المستلم', 'error'); return; }
      this.transferring = true;
      try {
        const res = await this.request('POST', '/assets/' + this.viewAssetId + '/transfer', {
          to_employee_id: this.transferEmployeeId,
          notes: this.transferNotes || undefined
        });
        if (res) {
          this.transferModalOpen = false;
          this.showToast('تم النقل بنجاح');
          this.loadAssetDetail(this.viewAssetId);
          if (this.transferCreateHandover) {
            const handoverRes = await this.request('POST', '/documents/handover', {
              asset_id: this.viewAssetId,
              employee_id: this.transferEmployeeId
            });
            if (handoverRes) this.showToast('تم النقل وإنشاء مستند التسليم (التعهد)');
            else this.showToast('تم النقل؛ فشل إنشاء مستند التسليم', 'error');
          }
        } else this.showToast('فشل النقل', 'error');
      } finally {
        this.transferring = false;
      }
    },
    async doReturnAsset() {
      const res = await this.request('POST', '/assets/' + this.viewAssetId + '/return');
      if (res) { this.showToast('تم الإرجاع'); this.loadAssetDetail(this.viewAssetId); }
      else this.showToast(this.lastErrorMsg || 'فشل الإرجاع', 'error');
    },
    async doSendMaintenance() {
      const res = await this.request('POST', '/assets/' + this.viewAssetId + '/maintenance', { notes: null });
      if (res) { this.showToast('تم إرسال الأصل للصيانة'); this.loadAssetDetail(this.viewAssetId); }
      else this.showToast(this.lastErrorMsg || 'فشل إرسال للصيانة', 'error');
    },
    async doReturnFromMaintenance() {
      const res = await this.request('POST', '/assets/' + this.viewAssetId + '/maintenance/return');
      if (res) { this.showToast('تم استلام الأصل من الصيانة'); this.loadAssetDetail(this.viewAssetId); }
      else this.showToast(this.lastErrorMsg || 'فشل استلام من الصيانة', 'error');
    },
    async doMarkLost() {
      if (!confirm('هل أنت متأكد من تسجيل هذا الأصل كمفقود؟')) return;
      const res = await this.request('POST', '/assets/' + this.viewAssetId + '/mark-lost', { notes: null });
      if (res) { this.showToast('تم التسجيل كمفقود'); this.loadAssetDetail(this.viewAssetId); }
      else this.showToast(this.lastErrorMsg || 'فشل التسجيل كمفقود', 'error');
    },
    async doRetireAsset() {
      if (!confirm('هل أنت متأكد من إستبعاد هذا الأصل؟')) return;
      const res = await this.request('POST', '/assets/' + this.viewAssetId + '/retire', { notes: null });
      if (res) { this.showToast('تم الإستبعاد'); this.loadAssetDetail(this.viewAssetId); }
      else this.showToast(this.lastErrorMsg || 'فشل الإستبعاد', 'error');
    },
    async loadAudits() {
      this.loadingAudits = true;
      try {
        let path = '/audits?limit=50';
        if (this.auditsCompanyId) path += '&company_id=' + this.auditsCompanyId;
        const res = await this.request('GET', path);
        this.auditsList = Array.isArray(res) ? res : [];
      } finally {
        this.loadingAudits = false;
      }
    },
    async loadBranchesForAudit() {
      if (!this.newAuditCompanyId) { this.branchesForAudit = []; return; }
      const res = await this.request('GET', '/branches?company_id=' + this.newAuditCompanyId + '&page=1&page_size=100');
      this.branchesForAudit = (res && res.items) ? res.items : [];
      this.newAuditBranchId = '';
    },
    async startAudit() {
      if (!this.newAuditCompanyId) { this.showToast('يرجى اختيار الشركة', 'error'); return; }
      const body = { company_id: this.newAuditCompanyId, branch_id: this.newAuditBranchId || null };
      this.savingAudit = true;
      try {
        const res = await this.request('POST', '/audits', body);
        if (res) { this.showToast('تم بدء جلسة التدقيق'); this.auditModalOpen = false; this.newAuditCompanyId = ''; this.newAuditBranchId = ''; this.loadAudits(); }
        else this.showToast(this.lastErrorMsg || 'فشل بدء التدقيق', 'error');
      } finally { this.savingAudit = false; }
    },
    async endAudit(auditId) {
      if (!confirm('هل أنت متأكد من إنهاء جلسة التدقيق؟')) return;
      const res = await this.request('POST', '/audits/' + auditId + '/end');
      if (res) { this.showToast('تم إنهاء الجلسة'); this.loadAudits(); }
      else this.showToast(this.lastErrorMsg || 'فشل إنهاء الجلسة', 'error');
    },
    async recordScan() {
      const assetId = (this.scanAssetIdInput || '').trim();
      if (!assetId) { this.showToast('يرجى إدخال معرّف الأصل', 'error'); return; }
      if (!this.scanAuditId) { this.showToast('لم تُحدد جلسة التدقيق', 'error'); return; }
      this.scanning = true;
      try {
        const res = await this.request('POST', '/audits/' + this.scanAuditId + '/scan', { asset_id: assetId });
        if (res) { this.showToast('تم تسجيل المسح'); this.scanModalOpen = false; this.scanAssetIdInput = ''; }
        else this.showToast(this.lastErrorMsg || 'فشل تسجيل المسح', 'error');
      } finally {
        this.scanning = false;
      }
    },
    async downloadAuditReport(auditId) {
      this.downloadingAuditId = auditId;
      try {
        const url = this.apiBase + '/audits/' + auditId + '/report/pdf';
        const r = await fetch(url, { headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {} });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل التحميل', 'error'); return; }
        const blob = await r.blob();
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'audit-report-' + auditId + '.pdf'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم التحميل');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل التحميل.', 'error');
      } finally {
        this.downloadingAuditId = null;
      }
    },
    async downloadDocument(docId) {
      this.downloadingDocumentId = docId;
      try {
        const url = this.apiBase + '/documents/' + docId + '/download';
        const r = await fetch(url, { headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {} });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل التحميل', 'error'); return; }
        const blob = await r.blob();
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'document-' + docId + '.pdf'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم التحميل');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل التحميل.', 'error');
      } finally {
        this.downloadingDocumentId = null;
      }
    },
    async openHandoverPreview(docId) {
      try {
        const url = this.apiBase + '/documents/' + docId + '/preview';
        const r = await fetch(url, { headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {} });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل فتح المعاينة', 'error'); return; }
        const html = await r.text();
        const w = window.open('', '_blank');
        if (w) { w.document.write(html); w.document.close(); } else this.showToast('السماح بالنوافذ المنبثقة للمعاينة', 'error');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل فتح المعاينة.', 'error');
      }
    },
    async loadDocuments() {
      if (!this.documentsAssetId) { this.documentsList = []; return; }
      this.loadingDocuments = true;
      try {
        const res = await this.request('GET', '/documents?asset_id=' + this.documentsAssetId);
        this.documentsList = Array.isArray(res) ? res : [];
      } finally {
        this.loadingDocuments = false;
      }
    },
    async loadDocumentsData() {
      if (!this.documentsCompanyId) { this.documentsAssetsList = []; this.documentsEmployeesList = []; return; }
      this.loadingDocumentsData = true;
      try {
        const [assetsRes, empRes] = await Promise.all([
          this.request('GET', '/assets?company_id=' + this.documentsCompanyId + '&page=1&page_size=200'),
          this.request('GET', '/employees?company_id=' + this.documentsCompanyId + '&page=1&page_size=200')
        ]);
        this.documentsAssetsList = (assetsRes && assetsRes.items) ? assetsRes.items : [];
        this.documentsEmployeesList = (empRes && empRes.items) ? empRes.items : [];
      } finally {
        this.loadingDocumentsData = false;
      }
    },
    async createHandover() {
      if (!this.handoverAssetId) { this.showToast('يرجى اختيار الأصل', 'error'); return; }
      if (!this.handoverEmployeeId) { this.showToast('يرجى اختيار الموظف', 'error'); return; }
      this.savingHandover = true;
      try {
        const res = await this.request('POST', '/documents/handover', { asset_id: this.handoverAssetId, employee_id: this.handoverEmployeeId });
        if (res) { this.showToast('تم إنشاء مستند التسليم'); this.documentsAssetId = this.handoverAssetId; this.loadDocuments(); }
        else this.showToast(this.lastErrorMsg || 'فشل إنشاء المستند', 'error');
      } finally { this.savingHandover = false; }
    },
    async loadAlerts() {
      if (!this.alertsCompanyId) { this.alerts = { needing_maintenance: [], warranty_expiring_this_month: [], lost: [] }; return; }
      this.loadingAlerts = true;
      try {
        const res = await this.request('GET', '/alerts?company_id=' + this.alertsCompanyId);
        this.alerts = res || { needing_maintenance: [], warranty_expiring_this_month: [], lost: [] };
      } finally {
        this.loadingAlerts = false;
      }
    },
    async loadMaintenanceAssets() {
      if (!this.maintenanceCompanyId) { this.maintenanceAssets = { items: [] }; return; }
      this.loadingMaintenance = true;
      try {
        const res = await this.request('GET', '/assets?company_id=' + this.maintenanceCompanyId + '&status=maintenance&page=1&page_size=200');
        this.maintenanceAssets = (res && res.items) ? res : { items: [] };
      } finally {
        this.loadingMaintenance = false;
      }
    },
    async loadLogs() {
      this.loadingLogs = true;
      try {
        const res = await this.request('GET', '/logs?page=1&page_size=50');
        this.logs = (res && res.items) ? res : { items: [], total: 0 };
      } finally {
        this.loadingLogs = false;
      }
    },
    async exportBackup() {
      this.exportingBackup = true;
      try {
        const url = this.apiBase + '/backup/export';
        const r = await fetch(url, { method: 'POST', headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {} });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل التصدير', 'error'); return; }
        const blob = await r.blob();
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'gacms-backup-' + new Date().toISOString().slice(0,10) + '.zip'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تنزيل النسخة الاحتياطية');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل تصدير النسخة الاحتياطية.', 'error');
      } finally {
        this.exportingBackup = false;
      }
    },
    async restoreBackup(file) {
      if (!file || !file.name.toLowerCase().endsWith('.zip')) { this.showToast('اختر ملف ZIP', 'error'); return; }
      this.restoringBackup = true;
      try {
        const form = new FormData(); form.append('file', file);
        const r = await fetch(this.apiBase + '/backup/restore', { method: 'POST', headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {}, body: form });
        const data = await r.json().catch(() => ({}));
        if (r.ok && (data.message || data.success)) { this.showToast('تم الاستعادة بنجاح'); setTimeout(() => location.reload(), 1500); }
        else this.showToast(data.detail || (data.errors && data.errors.join(', ')) || 'فشل الاستعادة', 'error');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل استعادة النسخة الاحتياطية.', 'error');
      } finally {
        this.restoringBackup = false;
      }
    },
    async downloadAssetsCsv() {
      if (!this.reportsCompanyId) { this.showToast('يرجى اختيار الشركة', 'error'); return; }
      this.exportingCsv = true;
      try {
        const url = this.apiBase + '/assets/export?company_id=' + this.reportsCompanyId;
        const r = await fetch(url, { headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {} });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل التصدير', 'error'); return; }
        const blob = await r.blob();
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'assets.csv'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تحميل CSV');
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل التصدير.', 'error');
      } finally { this.exportingCsv = false; }
    },
    csvEscape(v) {
      if (v == null) return '';
      const s = String(v);
      return s.includes(',') || s.includes('"') || s.includes('\n') ? '"' + s.replace(/"/g, '""') + '"' : s;
    },
    async downloadGroupsCsv() {
      this.exportingCsv = true;
      try {
        const res = await this.request('GET', '/groups?page=1&page_size=1000');
        if (!res || !res.items) { this.showToast(this.lastErrorMsg || 'فشل تحميل البيانات', 'error'); return; }
        const items = res.items;
        const rows = [['id', 'name', 'created_at']];
        items.forEach(g => rows.push([g.id, g.name || '', (g.created_at || '').slice(0, 19)]));
        const csv = rows.map(r => r.map(this.csvEscape).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'groups.csv'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تحميل مجموعات CSV');
      } finally { this.exportingCsv = false; }
    },
    async downloadCompaniesCsv() {
      this.exportingCsv = true;
      try {
        await this.loadCompaniesAll();
        const items = this.companiesAll.items || [];
        const rows = [['id', 'name', 'group_id', 'logo_url', 'address', 'phone', 'email', 'website', 'created_at']];
        items.forEach(c => rows.push([
          c.id, c.name || '', c.group_id || '', c.logo_url || '', (c.address || '').replace(/\n/g, ' '),
          c.phone || '', c.email || '', c.website || '', (c.created_at || '').slice(0, 19)
        ]));
        const csv = rows.map(r => r.map(this.csvEscape).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'companies.csv'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تحميل شركات CSV');
      } finally { this.exportingCsv = false; }
    },
    async downloadBranchesCsv() {
      if (!this.reportsCompanyId) { this.showToast('يرجى اختيار الشركة', 'error'); return; }
      this.exportingCsv = true;
      try {
        const res = await this.request('GET', '/branches?company_id=' + this.reportsCompanyId + '&page=1&page_size=1000');
        if (!res || !res.items) { this.showToast(this.lastErrorMsg || 'فشل تحميل البيانات', 'error'); return; }
        const items = res.items;
        const rows = [['id', 'name', 'company_id', 'address', 'created_at']];
        items.forEach(b => rows.push([
          b.id, b.name || '', b.company_id || '', (b.address || '').replace(/\n/g, ' '), (b.created_at || '').slice(0, 19)
        ]));
        const csv = rows.map(r => r.map(this.csvEscape).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'branches.csv'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تحميل فروع CSV');
      } finally { this.exportingCsv = false; }
    },
    async downloadEmployeesCsv() {
      if (!this.reportsCompanyId) { this.showToast('يرجى اختيار الشركة', 'error'); return; }
      this.exportingCsv = true;
      try {
        const res = await this.request('GET', '/employees?company_id=' + this.reportsCompanyId + '&page=1&page_size=1000');
        if (!res || !res.items) { this.showToast(this.lastErrorMsg || 'فشل تحميل البيانات', 'error'); return; }
        const items = res.items;
        const rows = [['id', 'name', 'national_id', 'job_title', 'department', 'status', 'company_id', 'branch_id', 'created_at']];
        items.forEach(e => rows.push([
          e.id, e.name || '', e.national_id || '', e.job_title || '', e.department || '', e.status || '',
          e.company_id || '', e.branch_id || '', (e.created_at || '').slice(0, 19)
        ]));
        const csv = rows.map(r => r.map(this.csvEscape).join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'employees.csv'; a.click(); URL.revokeObjectURL(a.href);
        this.showToast('تم تحميل موظفين CSV');
      } finally { this.exportingCsv = false; }
    },
    async loadUsers() {
      this.loadingUsers = true;
      try {
        let path = '/users?page=1&page_size=100';
        if (this.usersCompanyId) path += '&company_id=' + this.usersCompanyId;
        if (this.includeDeletedUsers) path += '&include_deleted=true';
        const res = await this.request('GET', path);
        if (res && res.items) this.usersList = res;
        else this.usersList = { items: [], total: 0 };
      } finally {
        this.loadingUsers = false;
      }
    },
    openUserModal(u = null) {
      this.closeAllModals();
      this.editingUser = u;
      this.userForm = { email: u ? u.email : '', password: '', company_id: u && u.company_id ? u.company_id : (this.usersCompanyId || ''), role: u ? u.role : 'company_admin' };
      this.userModalOpen = true;
    },
    async saveUser() {
      const email = (this.userForm.email || '').trim();
      if (!email) { this.showToast('يرجى إدخال البريد الإلكتروني', 'error'); return; }
      if (this.editingUser) {
        this.savingUser = true;
        try {
          const payload = { email, role: this.userForm.role };
          if (this.userForm.password && this.userForm.password.length >= 8) payload.password = this.userForm.password;
          const res = await this.request('PATCH', '/users/' + this.editingUser.id, payload);
          if (res) { this.showToast('تم التحديث'); this.userModalOpen = false; this.loadUsers(); }
          else this.showToast(this.lastErrorMsg || 'فشل تحديث المستخدم', 'error');
        } finally { this.savingUser = false; }
      } else {
        const password = (this.userForm.password || '').trim();
        if (!password) { this.showToast('يرجى إدخال كلمة المرور', 'error'); return; }
        if (password.length < 8) { this.showToast('كلمة المرور 8 أحرف على الأقل', 'error'); return; }
        this.savingUser = true;
        try {
          const res = await this.request('POST', '/users', {
            email,
            password,
            company_id: this.userForm.company_id || null,
            role: this.userForm.role
          });
          if (res) { this.showToast('تمت إضافة المستخدم'); this.userModalOpen = false; this.loadUsers(); }
          else this.showToast(this.lastErrorMsg || 'فشل إضافة المستخدم', 'error');
        } finally { this.savingUser = false; }
      }
    },
    async deleteUser(id) {
      if (!confirm('هل أنت متأكد من حذف هذا المستخدم؟')) return;
      const res = await this.request('DELETE', '/users/' + id);
      if (res != null) { this.showToast('تم الحذف'); this.loadUsers(); } else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },
    async restoreUser(id) {
      const res = await this.request('POST', '/users/' + id + '/restore');
      if (res) { this.showToast('تمت الاستعادة'); this.loadUsers(); } else this.showToast(this.lastErrorMsg || 'فشل الاستعادة', 'error');
    },
    async loadDashboard() {
      this.loadingDashboard = true;
      this.dashboard = { groupsCount: 0, companiesCount: 0, totalAssets: 0, alertsCount: 0, branchesCount: 0, employeesCount: 0, maintenanceCount: 0, lostCount: 0, warrantyCount: 0, byCompany: [] };
      try {
        const g = await this.request('GET', '/groups?page=1&page_size=1');
        this.dashboard.groupsCount = g && g.total != null ? g.total : 0;
        await this.loadCompaniesAll();
      this.dashboard.companiesCount = this.companiesAll.items.length;
      let totalAssets = 0;
      let totalBranches = 0;
      let totalEmployees = 0;
      let maintenanceCount = 0;
      let lostCount = 0;
      let warrantyCount = 0;
      const byCompany = [];
      for (const c of this.companiesAll.items) {
        const [a, b, e, dash] = await Promise.all([
          this.request('GET', '/assets?company_id=' + c.id + '&page=1&page_size=1'),
          this.request('GET', '/branches?company_id=' + c.id + '&page=1&page_size=1'),
          this.request('GET', '/employees?company_id=' + c.id + '&page=1&page_size=1'),
          this.request('GET', '/dashboard/company/' + c.id)
        ]);
        if (a && a.total) totalAssets += a.total;
        if (b && b.total) totalBranches += b.total;
        if (e && e.total) totalEmployees += e.total;
        if (dash) {
          if (dash.maintenance_count) maintenanceCount += dash.maintenance_count;
          if (dash.lost_count) lostCount += dash.lost_count;
          if (dash.warranty_expiring_this_month) warrantyCount += dash.warranty_expiring_this_month;
          byCompany.push({ name: c.name, asset_count: dash.total_assets || 0, book_value: dash.total_book_value || 0 });
        }
      }
      this.dashboard.totalAssets = totalAssets;
      this.dashboard.branchesCount = totalBranches;
      this.dashboard.employeesCount = totalEmployees;
      this.dashboard.maintenanceCount = maintenanceCount;
      this.dashboard.lostCount = lostCount;
      this.dashboard.warrantyCount = warrantyCount;
      this.dashboard.byCompany = byCompany;
      if (this.companiesAll.items.length && this.alertsCompanyId) await this.loadAlerts();
      else if (this.companiesAll.items.length) { this.alertsCompanyId = this.companiesAll.items[0].id; await this.loadAlerts(); }
      const al = (this.alerts.needing_maintenance || []).length + (this.alerts.lost || []).length + (this.alerts.warranty_expiring_this_month || []).length;
      this.dashboard.alertsCount = al;
      } finally {
        this.loadingDashboard = false;
      }
    },

    openGroupModal(g = null) {
      this.closeAllModals();
      this.editingGroup = g;
      this.groupForm = { name: g ? g.name : '' };
      this.groupModalOpen = true;
    },
    async saveGroup() {
      const name = (this.groupForm.name || '').trim();
      if (!name) {
        this.showToast('يرجى إدخال اسم المجموعة', 'error');
        return;
      }
      if (this.editingGroup) {
        this.savingGroup = true;
        try {
          const res = await this.request('PATCH', '/groups/' + this.editingGroup.id, { name });
          if (res) { this.showToast('تم التحديث'); this.groupModalOpen = false; await this.loadGroups(); }
          else this.showToast(this.lastErrorMsg || 'فشل التحديث', 'error');
        } finally { this.savingGroup = false; }
      } else {
        this.savingGroup = true;
        try {
          const res = await this.request('POST', '/groups', { name });
          if (res) {
            this.showToast('تمت الإضافة');
            this.groupModalOpen = false;
            this.groups.items = [res, ...(this.groups.items || [])];
            this.groups.total = (this.groups.total || 0) + 1;
          } else this.showToast(this.lastErrorMsg || 'فشل الإضافة', 'error');
        } finally { this.savingGroup = false; }
      }
    },
    async deleteGroup(id) {
      if (!confirm('هل أنت متأكد من حذف هذه المجموعة؟')) return;
      const res = await this.request('DELETE', '/groups/' + id);
      if (res != null) { this.showToast('تم الحذف'); this.loadGroups(); }
      else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },

    openCompanyModal(c = null) {
      this.closeAllModals();
      this.editingCompany = c;
      this.companyForm = {
        name: c ? c.name : '',
        logo_url: c ? c.logo_url || '' : '',
        primary_color: c ? c.primary_color || '#2563eb' : '#2563eb',
        legal_text: c ? c.legal_text || '' : '',
        address: c ? c.address || '' : '',
        phone: c ? c.phone || '' : '',
        email: c ? c.email || '' : '',
        website: c ? c.website || '' : ''
      };
      this.companyModalOpen = true;
    },
    async saveCompany() {
      const name = (this.companyForm.name || '').trim();
      if (!name) { this.showToast('يرجى إدخال اسم الشركة', 'error'); return; }
      let res;
      this.savingCompany = true;
      try {
        if (this.editingCompany) {
          res = await this.request('PATCH', '/companies/' + this.editingCompany.id, { ...this.companyForm, name });
        } else {
          res = await this.request('POST', '/companies', { group_id: this.companiesGroupId, ...this.companyForm, name });
        }
        if (res) {
          this.showToast(this.editingCompany ? 'تم التحديث' : 'تمت الإضافة');
          this.companyModalOpen = false;
          await this.loadCompanies();
          await this.loadCompaniesAll();
        } else this.showToast(this.lastErrorMsg || 'فشل في الحفظ', 'error');
      } finally { this.savingCompany = false; }
    },
    async uploadCompanyLogo(file) {
      if (!file || !this.editingCompany) return;
      const form = new FormData();
      form.append('file', file);
      try {
        const r = await fetch(this.apiBase + '/companies/' + this.editingCompany.id + '/logo', {
          method: 'POST',
          headers: this.token ? { 'Authorization': 'Bearer ' + this.token } : {},
          body: form
        });
        if (!r.ok) { const msg = await this.getFetchErrorMsg(r); this.showToast(msg || 'فشل رفع الشعار', 'error'); return; }
        const res = await r.json();
        if (res && res.logo_url) { this.companyForm.logo_url = res.logo_url; this.showToast('تم رفع الشعار'); }
      } catch (_) {
        this.showToast('خطأ في الاتصال. فشل رفع الشعار.', 'error');
      }
    },
    async deleteCompany(id) {
      if (!confirm('هل أنت متأكد من حذف هذه الشركة؟')) return;
      const res = await this.request('DELETE', '/companies/' + id);
      if (res != null) { this.loadCompanies(); this.loadCompaniesAll(); this.showToast('تم الحذف'); }
      else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },

    openBranchModal(b = null) {
      this.closeAllModals();
      this.editingBranch = b;
      this.branchForm = { name: b ? b.name : '', address: b ? b.address || '' : '' };
      this.branchModalOpen = true;
    },
    async saveBranch() {
      const name = (this.branchForm.name || '').trim();
      if (!name) { this.showToast('يرجى إدخال اسم الفرع', 'error'); return; }
      let res;
      this.savingBranch = true;
      try {
        if (this.editingBranch) {
          res = await this.request('PATCH', '/branches/' + this.editingBranch.id, { ...this.branchForm, name });
        } else {
          res = await this.request('POST', '/branches', { company_id: this.branchesCompanyId, ...this.branchForm, name });
        }
        if (res) {
            this.showToast(this.editingBranch ? 'تم التحديث' : 'تمت الإضافة');
            this.branchModalOpen = false;
            await this.loadBranches();
            await this.loadBranchesForEmployees();
          } else this.showToast(this.lastErrorMsg || 'فشل في الحفظ', 'error');
      } finally { this.savingBranch = false; }
    },
    async deleteBranch(id) {
      if (!confirm('هل أنت متأكد من حذف هذا الفرع؟')) return;
      const res = await this.request('DELETE', '/branches/' + id);
      if (res != null) { this.loadBranches(); this.loadBranchesForEmployees(); this.showToast('تم الحذف'); }
      else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },

    openEmployeeModal(e = null) {
      this.closeAllModals();
      this.editingEmployee = e;
      this.employeeForm = {
        name: e ? e.name : '',
        national_id: e ? e.national_id || '' : '',
        job_title: e ? e.job_title || '' : '',
        department: e ? e.department || '' : '',
        status: e ? e.status : 'active'
      };
      this.employeeModalOpen = true;
    },
    async saveEmployee() {
      const name = (this.employeeForm.name || '').trim();
      if (!name) { this.showToast('يرجى إدخال اسم الموظف', 'error'); return; }
      let res;
      this.savingEmployee = true;
      try {
        if (this.editingEmployee) {
          res = await this.request('PATCH', '/employees/' + this.editingEmployee.id, { ...this.employeeForm, name });
        } else {
          res = await this.request('POST', '/employees', {
            company_id: this.employeesCompanyId,
            branch_id: this.employeesBranchId,
            ...this.employeeForm,
            name
          });
        }
        if (res) { this.showToast(this.editingEmployee ? 'تم التحديث' : 'تمت الإضافة'); this.employeeModalOpen = false; this.loadEmployees(); }
        else this.showToast(this.lastErrorMsg || 'فشل في الحفظ', 'error');
      } finally { this.savingEmployee = false; }
    },
    async deleteEmployee(id) {
      if (!confirm('هل أنت متأكد من حذف هذا الموظف؟')) return;
      const res = await this.request('DELETE', '/employees/' + id);
      if (res != null) { this.showToast('تم الحذف'); this.loadEmployees(); }
      else this.showToast(this.lastErrorMsg || 'فشل الحذف', 'error');
    },

    openAssetModal(a = null) {
      this.closeAllModals();
      this.editingAsset = a;
      const spec = (a && a.specifications && typeof a.specifications === 'object') ? { ...a.specifications } : {};
      this.assetForm = {
        type: a ? a.type : 'laptop',
        brand: a ? a.brand || '' : '',
        model: a ? a.model || '' : '',
        serial_number: a ? a.serial_number || '' : '',
        status: a ? a.status : 'active',
        specifications: spec,
        notes: (spec.notes != null && spec.notes !== '') ? String(spec.notes) : ''
      };
      this.assetModalOpen = true;
    },
    specFieldsForType(type) {
      return this.ASSET_SPEC_FIELDS[type] || [];
    },
    assetTypeNameAr(type) {
      const names = { laptop: 'لابتوب', mobile: 'موبايل', tablet: 'تابلت', desktop: 'كمبيوتر مكتبي', monitor: 'شاشة', peripheral: 'ملحق', printer: 'طابعة', other: 'أخرى' };
      return names[type] || type;
    },
    async saveAsset() {
      const spec = {};
      (this.ASSET_SPEC_FIELDS[this.assetForm.type] || []).forEach(f => {
        const v = this.assetForm.specifications[f.key];
        if (v != null && String(v).trim() !== '') spec[f.key] = String(v).trim();
      });
      if (this.assetForm.notes != null && String(this.assetForm.notes).trim() !== '') spec.notes = String(this.assetForm.notes).trim();
      const payload = {
        type: this.assetForm.type,
        brand: this.assetForm.brand || null,
        model: this.assetForm.model || null,
        serial_number: this.assetForm.serial_number || null,
        status: this.assetForm.status,
        specifications: Object.keys(spec).length ? spec : null
      };
      let res;
      this.savingAsset = true;
      try {
        if (this.editingAsset) {
          res = await this.request('PATCH', '/assets/' + this.editingAsset.id, payload);
        } else {
          const br = await this.request('GET', '/branches?company_id=' + this.assetsCompanyId + '&page=1&page_size=1');
          const branchId = br && br.items && br.items[0] ? br.items[0].id : null;
          if (!branchId) { this.showToast('يجب وجود فرع واحد على الأقل للشركة المختارة', 'error'); return; }
          res = await this.request('POST', '/assets', {
            company_id: this.assetsCompanyId,
            branch_id: branchId,
            ...payload
          });
        }
        if (res) { this.showToast(this.editingAsset ? 'تم التحديث' : 'تمت الإضافة'); this.assetModalOpen = false; this.loadAssets(); if (this.viewAssetId && this.editingAsset && this.editingAsset.id === this.viewAssetId) this.loadAssetDetail(this.viewAssetId); }
        else this.showToast(this.lastErrorMsg || 'فشل في الحفظ', 'error');
      } finally { this.savingAsset = false; }
    },
    statusClass(s) {
      if (s === 'active') return 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300';
      if (s === 'maintenance') return 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300';
      if (s === 'lost') return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300';
      if (s === 'retired') return 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300';
      return 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400';
    },

    onRouteChange() {
      if (!this.token) return;
      document.title = (this.pageTitle || 'STC GACMS') + ' - STC GACMS';
      const parts = this.route.split('/').filter(Boolean);
      const r = parts[0] || '';
      if (this.route === '/') this.loadDashboard();
      else if (r === 'groups') this.loadGroups();
      else if (r === 'companies') this.loadCompanies();
      else if (r === 'branches') {
        (async () => { await this.loadCompaniesAll(); this.loadBranches(); })();
      }
      else if (r === 'employees') {
        (async () => { await this.loadCompaniesAll(); this.loadBranchesForEmployees(); this.loadEmployees(); })();
      }
      else if (r === 'assets') {
        (async () => {
          await this.loadCompaniesAll();
          const assetId = parts[1] && parts[1].length > 10 ? parts[1] : null;
          if (assetId) { this.viewAssetId = assetId; this.loadAssetDetail(assetId); }
          else { this.viewAssetId = null; this.loadAssets(); }
        })();
      }
      else if (r === 'alerts') {
        (async () => { await this.loadCompaniesAll(); this.loadAlerts(); })();
      }
      else if (r === 'maintenance') {
        (async () => { await this.loadCompaniesAll(); this.loadMaintenanceAssets(); })();
      }
      else if (r === 'logs') this.loadLogs();
      else if (r === 'audits') {
        (async () => { await this.loadCompaniesAll(); this.loadAudits(); })();
      }
      else if (r === 'documents') {
        (async () => {
          await this.loadCompaniesAll();
          this.documentsCompanyId = '';
          this.documentsAssetId = '';
          this.documentsList = [];
          this.documentsAssetsList = [];
          this.documentsEmployeesList = [];
        })();
      }
      else if (r === 'reports' || r === 'settings') {
        (async () => { await this.loadCompaniesAll(); })();
        if (this.route === '/settings') this.loadSettingsAssetSpecJson();
      }
      else if (r === 'users') {
        (async () => { await this.loadCompaniesAll(); this.loadUsers(); })();
      }
    },
    init() {
      this.route = '/';
      this.viewAssetId = null;
      window.__gacmsApp = this;
      try {
        const stored = localStorage.getItem('gacms_asset_spec_fields');
        if (stored) { const parsed = JSON.parse(stored); if (parsed && typeof parsed === 'object') this.ASSET_SPEC_FIELDS = parsed; }
      } catch (_) {}
      try {
        const labels = localStorage.getItem('gacms_alert_labels');
        if (labels) { const parsed = JSON.parse(labels); if (parsed && typeof parsed === 'object') this.alertLabels = { ...this.alertLabels, ...parsed }; }
      } catch (_) {}
      this.token = localStorage.getItem('gacms_token') || '';
      if (!this.token) return;
      this.route = '/';
      this.routeReady = true;
      (async () => {
        await this.loadGroups();
        await this.loadCompaniesAll();
        this.onRouteChange();
      })();
    },
    /** معالج مركزي لفتح النوافذ من الأحداث (حل جذري لضمان عمل الأزرار) */
    handleOpenModal(detail) {
      if (!detail || !detail.modal) return;
      const { modal, item } = detail;
      if (modal === 'group') this.openGroupModal(item || null);
      else if (modal === 'company') this.openCompanyModal(item || null);
      else if (modal === 'branch') this.openBranchModal(item || null);
      else if (modal === 'employee') this.openEmployeeModal(item || null);
      else if (modal === 'asset') this.openAssetModal(item || null);
      else if (modal === 'user') {
        this.openUserModal(item || null);
        if (!item && detail.companyId) this.userForm.company_id = detail.companyId;
      }
      else if (modal === 'assign') this.openAssignModal();
      else if (modal === 'transfer') this.openTransferModal();
      else if (modal === 'audit') { this.closeAllModals(); this.auditModalOpen = true; this.loadCompaniesAll(); this.loadBranchesForAudit(); }
      else if (modal === 'handover-preview' && detail.id) this.openHandoverPreview(detail.id);
    },
    /** معالج مركزي للحذف */
    handleDelete(detail) {
      if (!detail || !detail.type || !detail.id) return;
      if (detail.type === 'group') this.deleteGroup(detail.id);
      else if (detail.type === 'company') this.deleteCompany(detail.id);
      else if (detail.type === 'branch') this.deleteBranch(detail.id);
      else if (detail.type === 'employee') this.deleteEmployee(detail.id);
      else if (detail.type === 'asset') this.deleteAsset(detail.id);
      else if (detail.type === 'user') this.deleteUser(detail.id);
    },
    /** معالج مركزي للاستعادة */
    handleRestore(detail) {
      if (!detail || !detail.type || !detail.id) return;
      if (detail.type === 'group') this.restoreGroup(detail.id);
      else if (detail.type === 'company') this.restoreCompany(detail.id);
      else if (detail.type === 'branch') this.restoreBranch(detail.id);
      else if (detail.type === 'employee') this.restoreEmployee(detail.id);
      else if (detail.type === 'asset') this.restoreAsset(detail.id);
      else if (detail.type === 'user') this.restoreUser(detail.id);
    },
    saveAlertLabels() {
      this.savingSettingsAlerts = true;
      try {
        localStorage.setItem('gacms_alert_labels', JSON.stringify(this.alertLabels));
        this.showToast('تم حفظ تسميات التنبيهات');
      } finally {
        this.savingSettingsAlerts = false;
      }
    },
    saveAssetSpecFields() {
      this.savingSettingsSpecs = true;
      try {
        const parsed = JSON.parse(this.settingsAssetSpecJson || '{}');
        if (parsed && typeof parsed === 'object') {
          this.ASSET_SPEC_FIELDS = parsed;
          localStorage.setItem('gacms_asset_spec_fields', JSON.stringify(parsed));
          this.showToast('تم حفظ حقول أنواع الأصول');
        } else this.showToast('صيغة JSON غير صحيحة', 'error');
      } catch (e) { this.showToast('صيغة JSON غير صحيحة', 'error'); }
      finally {
        this.savingSettingsSpecs = false;
      }
    },
    loadSettingsAssetSpecJson() {
      this.settingsAssetSpecJson = JSON.stringify(this.ASSET_SPEC_FIELDS, null, 2);
    }
  }));
});
