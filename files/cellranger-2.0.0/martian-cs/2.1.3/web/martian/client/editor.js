(function() {
  var app, initEditor, initSession, renderPipeline;

  app = angular.module('app', ['ui.bootstrap']);

  app.filter('shorten', function() {
    return function(s) {
      s = s + "";
      if (s.length < 21) {
        return s;
      } else {
        return s.substr(0, 10) + " ... " + s.substr(s.length - 10);
      }
    };
  });

  app.directive('pipeGraph', function() {
    return {
      restrict: 'A',
      scope: {
        pipelineDec: '=pipelineDec'
      },
      link: function(scope, element, attrs) {
        return scope.$watch(attrs.style, function(value) {
          return renderPipeline(scope.pipelineDec);
        });
      }
    };
  });

  renderPipeline = function(pipelineDec) {
    var bindStm, callStm, g, i, j, k, len, len1, len2, ref, ref1, ref2, valueExp;
    g = new dagreD3.Digraph();
    ref = pipelineDec.Calls;
    for (i = 0, len = ref.length; i < len; i++) {
      callStm = ref[i];
      g.addNode(callStm.Id, {
        label: callStm.Id
      });
    }
    ref1 = pipelineDec.Calls;
    for (j = 0, len1 = ref1.length; j < len1; j++) {
      callStm = ref1[j];
      ref2 = callStm.Bindings.List;
      for (k = 0, len2 = ref2.length; k < len2; k++) {
        bindStm = ref2[k];
        valueExp = bindStm.Exp;
        if (valueExp.Kind === 'call') {
          g.addEdge(null, valueExp.Id, callStm.Id, {
            label: bindStm.Tname
          });
        }
      }
    }
    (new dagreD3.Renderer()).run(g, d3.select("g#" + pipelineDec.Id));
    d3.selectAll("g.node rect").each(function(id) {
      return d3.select(this).attr('rx', 20).attr('ry', 20);
    });
    return d3.selectAll("g.node").each(function(id) {
      return d3.select(this).classed('complete', true);
    });
  };

  app.directive('mainAceEditor', function() {
    return {
      restrict: 'E',
      scope: {
        editorInfo: '=editorInfo',
        save: '&save'
      },
      link: function(scope, element, attrs) {
        var e;
        scope.editorInfo.ace = e = initEditor(element[0]);
        e.setOptions({
          maxLines: 1000
        });
        e.on('change', function(e) {
          return scope.$apply(function() {
            return scope.editorInfo.dirty = true;
          });
        });
        e.commands.addCommand({
          name: 'Save',
          bindKey: {
            win: 'Ctrl-S',
            mac: 'Command-S'
          },
          exec: function(e) {
            return scope.save();
          },
          readOnly: false
        });
        return e.commands.addCommand({
          name: 'Undo',
          bindKey: {
            win: 'Ctrl-Z',
            mac: 'Command-Z'
          },
          exec: function(e) {
            return e.undo();
          },
          readOnly: false
        });
      }
    };
  });

  app.directive('includeAceEditor', function() {
    return {
      restrict: 'E',
      scope: {
        editorInfo: '=editorInfo'
      },
      link: function(scope, element, attrs) {
        var e;
        scope.editorInfo.ace = e = initEditor(element[0]);
        e.renderer.setShowGutter(false);
        return e.setReadOnly(true);
      }
    };
  });

  initEditor = function(elem) {
    var editor;
    editor = ace.edit(elem);
    editor.setTheme('ace/theme/clouds');
    editor.setShowFoldWidgets(false);
    editor.setHighlightActiveLine(false);
    return editor;
  };

  initSession = function(einfo, mroPath, fname, contents) {
    var session;
    session = new ace.EditSession(contents, 'ace/mode/coffee');
    session.setUseWorker(false);
    session.setUndoManager(new ace.UndoManager());
    einfo.ace.setSession(session);
    einfo.dirty = false;
    einfo.mroPath = mroPath;
    return einfo.fname = fname;
  };

  app.controller('MartianEdCtrl', function($scope, $http) {
    $scope.mroPaths = mroPaths;
    $scope.mroPath = mroPaths[0];
    $scope.mainEditor = {
      mroPath: $scope.mroPath,
      fname: 'select file:',
      dirty: false
    };
    $scope.includeEditor = {
      fname: ''
    };
    $scope.availableFiles = [];
    $http.get('/files').success(function(data) {
      return $scope.availableFiles = data;
    });
    $scope.selectMroPath = function(mroPath) {
      return $scope.mroPath = mroPath;
    };
    $scope.selectFile = function(file) {
      return $http.post('/load', {
        mroPath: file.mroPath,
        fname: file.fname
      }).success(function(data) {
        initSession($scope.mainEditor, file.mroPath, file.fname, data.contents);
        if (data.includeFile) {
          initSession($scope.includeEditor, data.includeFile.mroPath, data.includeFile.name, data.includeFile.contents);
        }
        $scope.compilerMessages = '';
        return $scope.pipelineDecList = [];
      });
    };
    $scope.selectTab = function(pipelineDec) {
      return renderPipeline(pipelineDec);
    };
    $scope.build = function() {
      if ($scope.mainEditor.fname === 'select file:') {
        window.alert('Select a file first.');
        return;
      }
      return $http.post('/build', {
        mroPath: $scope.mainEditor.mroPath,
        fname: $scope.mainEditor.fname
      }).success(function(data) {
        var filetypes, locMatch, ptree;
        if (typeof data === 'string') {
          locMatch = data.match(/on line (\d+):/);
          if (locMatch != null) {
            $scope.mainEditor.ace.gotoLine(parseInt(locMatch[1]));
          }
          $scope.compilerMessages = data;
          return $scope.pipelineDecList = [];
        } else {
          console.log(data);
          ptree = data;
          filetypes = _.keys(ptree.FiletypeTable);
          $scope.compilerMessages = "Build successful:\n" + ("    " + filetypes.length + " filetype declarations\n") + ("    " + ptree.Stages.length + " stage declarations\n") + ("    " + ptree.Pipelines.length + " pipeline declarations");
          $scope.pipelineDecList = ptree.Pipelines;
          if ($scope.pipelineDecList[0] != null) {
            return $scope.pipelineDecList[0].active = true;
          }
        }
      });
    };
    $scope["new"] = function() {
      var fname;
      fname = window.prompt('Enter file name including .mro extension:');
      if (!((fname != null) && fname.length > 0)) {
        return;
      }
      $scope.availableFiles.push({
        mroPath: $scope.mroPath,
        fname: fname
      });
      initSession($scope.mainEditor, $scope.mroPath, fname, '');
      initSession($scope.includeEditor, '', '', '');
      $scope.mainEditor.dirty = true;
      $scope.compileMessages = '';
      return $scope.pipelineDecList = [];
    };
    return $scope.save = function() {
      return $http.post('/save', {
        mroPath: $scope.mainEditor.mroPath,
        fname: $scope.mainEditor.fname,
        contents: $scope.mainEditor.ace.getValue()
      }).success(function(data) {
        return $scope.mainEditor.dirty = false;
      });
    };
  });

}).call(this);
