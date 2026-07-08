(() => {
  function findApi(win) {
    let tries = 0;
    while (win && tries < 12) {
      if (win.API_1484_11) return { api: win.API_1484_11, version: '2004' };
      if (win.API) return { api: win.API, version: '1.2' };
      win = win.parent && win.parent !== win ? win.parent : win.opener;
      tries += 1;
    }
    return null;
  }

  window.NumberSeaScorm = function createScormRuntime(storagePrefix) {
    const found = findApi(window);
    const api = found?.api || null;
    const version = found?.version || 'local';
    let connected = false;

    const call = (name, ...args) => {
      if (!api || typeof api[name] !== 'function') return '';
      try { return api[name](...args); } catch (error) { console.warn('SCORM call failed', name, error); return ''; }
    };
    const keyFor = (key) => `${storagePrefix}:${key}`;

    return {
      version,
      initialize() {
        if (api) {
          const result = call(version === '2004' ? 'Initialize' : 'LMSInitialize', '');
          connected = result === true || result === 'true';
        }
        return connected;
      },
      getValue(key) {
        if (connected) return call(version === '2004' ? 'GetValue' : 'LMSGetValue', key) || '';
        return localStorage.getItem(keyFor(key)) || '';
      },
      setValue(key, value) {
        if (connected) call(version === '2004' ? 'SetValue' : 'LMSSetValue', `${key}`, `${value}`);
        localStorage.setItem(keyFor(key), `${value}`);
      },
      commit() { if (connected) call(version === '2004' ? 'Commit' : 'LMSCommit', ''); },
      finish() { this.commit(); if (connected) call(version === '2004' ? 'Terminate' : 'LMSFinish', ''); },
      learnerName() {
        const name = this.getValue(version === '2004' ? 'cmi.learner_name' : 'cmi.core.student_name');
        return name || '小小探险家';
      },
      hydrate() {
        return {
          location: this.getValue(version === '2004' ? 'cmi.location' : 'cmi.core.lesson_location'),
          score: this.getValue(version === '2004' ? 'cmi.score.raw' : 'cmi.core.score.raw'),
          status: this.getValue(version === '2004' ? 'cmi.completion_status' : 'cmi.core.lesson_status'),
          suspendData: this.getValue('cmi.suspend_data')
        };
      },
      save(payload) {
        if (version === '2004') {
          this.setValue('cmi.location', payload.location);
          this.setValue('cmi.score.raw', payload.score);
          this.setValue('cmi.score.min', '0');
          this.setValue('cmi.score.max', payload.maxScore || '150');
          this.setValue('cmi.completion_status', payload.completionStatus);
          this.setValue('cmi.success_status', payload.successStatus);
          this.setValue('cmi.progress_measure', payload.progressMeasure);
        } else {
          this.setValue('cmi.core.lesson_location', payload.location);
          this.setValue('cmi.core.score.raw', payload.score);
          this.setValue('cmi.core.lesson_status', payload.completionStatus === 'completed' ? 'passed' : 'incomplete');
        }
        this.setValue('cmi.suspend_data', payload.suspendData);
        this.commit();
      }
    };
  };
})();
