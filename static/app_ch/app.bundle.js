/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 122);
/******/ })
/************************************************************************/
/******/ ({

/***/ 115:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

var _reactRouterDom = __webpack_require__(39);

var _Side_navbar = __webpack_require__(127);

var _Side_navbar2 = _interopRequireDefault(_Side_navbar);

var _base = __webpack_require__(67);

var _New_task = __webpack_require__(126);

var _New_task2 = _interopRequireDefault(_New_task);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Main_area = function (_React$Component) {
  _inherits(Main_area, _React$Component);

  function Main_area(props) {
    _classCallCheck(this, Main_area);

    return _possibleConstructorReturn(this, (Main_area.__proto__ || Object.getPrototypeOf(Main_area)).call(this, props));
  }

  _createClass(Main_area, [{
    key: 'render',
    value: function render() {
      return _react2.default.createElement(
        'div',
        { className: 'main_area container-fluid' },
        _react2.default.createElement(
          _reactRouterDom.BrowserRouter,
          null,
          _react2.default.createElement(
            'div',
            { className: 'row' },
            _react2.default.createElement(_Side_navbar2.default, null),
            _react2.default.createElement(
              'main',
              { className: 'col-sm-10 content' },
              _react2.default.createElement(_reactRouterDom.Route, { exact: true, path: '/home/ch/', component: _New_task2.default })
            )
          )
        )
      );
    }
  }]);

  return Main_area;
}(_react2.default.Component);

Main_area.propTypes = {};

Main_area.defaultProps = {};

exports.default = Main_area;

/***/ }),

/***/ 116:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Top_navbar = function (_React$Component) {
  _inherits(Top_navbar, _React$Component);

  function Top_navbar(props) {
    _classCallCheck(this, Top_navbar);

    return _possibleConstructorReturn(this, (Top_navbar.__proto__ || Object.getPrototypeOf(Top_navbar)).call(this, props));
  }

  _createClass(Top_navbar, [{
    key: 'render',
    value: function render() {
      return _react2.default.createElement(
        'nav',
        { className: 'navbar navbar-default fixed-top' },
        _react2.default.createElement(
          'div',
          { className: 'container-fluid' },
          _react2.default.createElement(
            'div',
            { className: 'navbar-header' },
            _react2.default.createElement(
              'button',
              { type: 'button', className: 'navbar-toggle collapsed', 'data-toggle': 'collapse', 'data-target': '#bs-example-navbar-collapse-1' },
              _react2.default.createElement(
                'span',
                { className: 'sr-only' },
                'Toggle navigation'
              ),
              _react2.default.createElement('span', { className: 'icon-bar' }),
              _react2.default.createElement('span', { className: 'icon-bar' }),
              _react2.default.createElement('span', { className: 'icon-bar' })
            ),
            _react2.default.createElement(
              'a',
              { className: 'navbar-brand', href: '#' },
              _react2.default.createElement(
                'small',
                null,
                '\u8BFA\u4E9A\u57FA\u56E0\u89E3\u8BFB\u5E73\u53F0 1.0'
              )
            )
          ),
          _react2.default.createElement(
            'div',
            { className: 'collapse navbar-collapse', id: 'bs-example-navbar-collapse-1' },
            _react2.default.createElement(
              'ul',
              { className: 'nav navbar-nav navbar-right' },
              _react2.default.createElement(
                'li',
                { className: 'dropdown' },
                _react2.default.createElement(
                  'a',
                  { href: '#', className: 'dropdown-toggle', 'data-toggle': 'dropdown', role: 'button', 'aria-expanded': 'false' },
                  '\u8BED\u8A00',
                  _react2.default.createElement('span', { className: 'caret' })
                ),
                _react2.default.createElement(
                  'ul',
                  { className: 'dropdown-menu', role: 'menu' },
                  _react2.default.createElement(
                    'li',
                    null,
                    _react2.default.createElement(
                      'a',
                      { href: '#' },
                      'English'
                    )
                  ),
                  _react2.default.createElement(
                    'li',
                    null,
                    _react2.default.createElement(
                      'a',
                      { href: '#' },
                      '\u4E2D\u6587'
                    )
                  )
                )
              ),
              _react2.default.createElement(
                'li',
                { className: 'dropdown' },
                _react2.default.createElement(
                  'a',
                  { href: '#', className: 'dropdown-toggle', 'data-toggle': 'dropdown', role: 'button', 'aria-expanded': 'false' },
                  '\u8D26\u6237 ',
                  _react2.default.createElement('span', { className: 'caret' })
                ),
                _react2.default.createElement(
                  'ul',
                  { className: 'dropdown-menu', role: 'menu' },
                  _react2.default.createElement(
                    'li',
                    null,
                    _react2.default.createElement(
                      'a',
                      { href: '#' },
                      '\u7528\u6237\u540D:test'
                    )
                  ),
                  _react2.default.createElement('li', { className: 'divider' }),
                  _react2.default.createElement(
                    'li',
                    null,
                    _react2.default.createElement(
                      'a',
                      { href: '#' },
                      '\u4FEE\u6539\u5BC6\u7801'
                    )
                  ),
                  _react2.default.createElement(
                    'li',
                    null,
                    _react2.default.createElement(
                      'a',
                      { href: '#' },
                      '\u9000\u51FA\u767B\u9646'
                    )
                  )
                )
              )
            )
          )
        )
      );
    }
  }]);

  return Top_navbar;
}(_react2.default.Component);

Top_navbar.propTypes = {};

Top_navbar.defaultProps = {};

exports.default = Top_navbar;

/***/ }),

/***/ 117:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _redux = __webpack_require__(64);

var _reduxLogger = __webpack_require__(274);

var _reduxThunk = __webpack_require__(275);

var _reduxThunk2 = _interopRequireDefault(_reduxThunk);

var _root_reducer = __webpack_require__(128);

var _root_reducer2 = _interopRequireDefault(_root_reducer);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

// Create the initial state
var initialState = {};

// Create redux store with middleware


// Import the neccerry root reducer
var logger = (0, _reduxLogger.createLogger)();
var createStoreWithMiddleware = (0, _redux.applyMiddleware)(_reduxThunk2.default)(_redux.createStore);
var store = createStoreWithMiddleware(_root_reducer2.default, initialState);

exports.default = store;

/***/ }),

/***/ 118:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/react-dom/index.js'\n    at Error (native)");

/***/ }),

/***/ 119:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/react-redux/es/index.js'\n    at Error (native)");

/***/ }),

/***/ 120:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(132);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(280)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../node_modules/css-loader/index.js!../node_modules/sass-loader/lib/loader.js!./root_style.scss", function() {
			var newContent = require("!!../node_modules/css-loader/index.js!../node_modules/sass-loader/lib/loader.js!./root_style.scss");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 121:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
var root_actions = {};

exports.default = root_actions;

/***/ }),

/***/ 122:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

var _reactDom = __webpack_require__(118);

var _reactDom2 = _interopRequireDefault(_reactDom);

var _reactRedux = __webpack_require__(119);

var _reactRouterDom = __webpack_require__(39);

var _createBrowserHistory = __webpack_require__(65);

var _createBrowserHistory2 = _interopRequireDefault(_createBrowserHistory);

var _reactRouterRedux = __webpack_require__(66);

__webpack_require__(120);

var _store = __webpack_require__(117);

var _store2 = _interopRequireDefault(_store);

var _Top_navbar = __webpack_require__(116);

var _Top_navbar2 = _interopRequireDefault(_Top_navbar);

var _Main_area = __webpack_require__(115);

var _Main_area2 = _interopRequireDefault(_Main_area);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

//create a history of choosing


// Import the main elements
var history = (0, _createBrowserHistory2.default)();

// Render the element into dom


// Import redux store
_reactDom2.default.render(_react2.default.createElement(
  _reactRedux.Provider,
  { store: _store2.default },
  _react2.default.createElement(
    _reactRouterRedux.ConnectedRouter,
    { history: history },
    _react2.default.createElement(
      'div',
      null,
      _react2.default.createElement(_reactRouterDom.Route, { path: '/home', component: _Top_navbar2.default }),
      _react2.default.createElement(_reactRouterDom.Route, { path: '/home', component: _Main_area2.default })
    )
  )
), document.getElementById('root'));

/***/ }),

/***/ 123:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

var _Progress_task = __webpack_require__(125);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var New_task_progress = function (_React$Component) {
  _inherits(New_task_progress, _React$Component);

  function New_task_progress(props) {
    _classCallCheck(this, New_task_progress);

    return _possibleConstructorReturn(this, (New_task_progress.__proto__ || Object.getPrototypeOf(New_task_progress)).call(this, props));
  }

  _createClass(New_task_progress, [{
    key: '_loadProgressList',
    value: function _loadProgressList(progress_list) {
      return progress_list.map(function (task, index) {
        if (index % 2 === 0) {
          return _react2.default.createElement(
            'div',
            { key: index, className: 'td3 td-stripe' },
            _react2.default.createElement(_Progress_task.Processing_task, null)
          );
        } else {
          return _react2.default.createElement(
            'div',
            { key: index, className: 'td3 ' },
            _react2.default.createElement(_Progress_task.Completed_task, null)
          );
        }
      });
    }
  }, {
    key: 'render',
    value: function render() {
      return _react2.default.createElement(
        'div',
        { className: 'new_task_progress' },
        _react2.default.createElement(
          'div',
          { className: 'tb-title' },
          '\u4E0A\u4F20\u5217\u8868:'
        ),
        this._loadProgressList(this.props.progress_list)
      );
    }
  }]);

  return New_task_progress;
}(_react2.default.Component);

New_task_progress.propTypes = {
  progress_list: _react2.default.PropTypes.array
};

New_task_progress.defaultProps = {
  progress_list: [1, 1, 1]
};

exports.default = New_task_progress;

/***/ }),

/***/ 124:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var New_task_upload = function (_React$Component) {
  _inherits(New_task_upload, _React$Component);

  function New_task_upload(props) {
    _classCallCheck(this, New_task_upload);

    var _this = _possibleConstructorReturn(this, (New_task_upload.__proto__ || Object.getPrototypeOf(New_task_upload)).call(this, props));

    _this.state = {
      father_check: false,
      father_check_pheno: false,
      mother_check: false,
      mother_check_pheno: false,
      incidental_findings_check: false,
      candidate_genes_check: false,
      input_gene_file: '尚未选择',
      input_phen: '尚未选择',
      father_gene_file: '尚未选择',
      mother_gene_file: '尚未选择'
    };
    return _this;
  }

  _createClass(New_task_upload, [{
    key: '_handleSubmit',
    value: function _handleSubmit() {
      alert('hahah submit yo!');
    }
  }, {
    key: '_handleChange',
    value: function _handleChange(evt) {
      var target = evt.target;

      if (target.nodeName === 'INPUT') {
        switch (target.id) {
          case 'input_gene_file':
            this.setState(_extends({}, this.state, { input_gene_file: target.files[0].name }));
            break;
          case 'input_phen':
            this.setState(_extends({}, this.state, { input_phen: target.files[0].name }));
            break;
          case 'father_gene_file':
            this.setState(_extends({}, this.state, { father_gene_file: target.files[0].name }));
            break;
          case 'mother_gene_file':
            this.setState(_extends({}, this.state, { mother_gene_file: target.files[0].name }));
            break;
          default:
            break;
        }
      }
    }
  }, {
    key: '_handleClick',
    value: function _handleClick(evt) {
      var target = evt.target;
      if (target.nodeName === 'LABEL') {
        switch (target.htmlFor) {
          case 'check_father':
            this.setState(_extends({}, this.state, { father_check: !this.state.father_check }));
            break;

          case 'check_father_pheno':
            this.setState(_extends({}, this.state, { father_check_pheno: !this.state.father_check_pheno }));
            break;

          case 'check_mother':
            this.setState(_extends({}, this.state, { mother_check: !this.state.mother_check }));
            break;

          case 'check_mother_pheno':
            this.setState(_extends({}, this.state, { mother_check_pheno: !this.state.mother_check_pheno }));
            break;

          case 'check_incidental_findings':
            this.setState(_extends({}, this.state, { incidental_findings_check: !this.state.incidental_findings_check }));
            break;

          case 'check_candidate_genes':
            this.setState(_extends({}, this.state, { candidate_genes_check: !this.state.candidate_genes_check }));
            break;

          default:
            break;
        }
      };
    }
  }, {
    key: 'render',
    value: function render() {
      var _this2 = this;

      return _react2.default.createElement(
        'div',
        { className: 'new_task_upload' },
        _react2.default.createElement(
          'form',
          { id: 'myForm', name: 'myForm', encType: 'multipart/form-data', onSubmit: function onSubmit() {
              return _this2._handleSubmit();
            } },
          _react2.default.createElement(
            'div',
            { className: 'form-tb' },
            _react2.default.createElement(
              'div',
              { className: 'tb-section' },
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement(
                  'div',
                  { className: 'td1' },
                  _react2.default.createElement(
                    'label',
                    { htmlFor: 'enter_task_name' },
                    '\u4EFB\u52A1\u540D\u79F0:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement('input', { id: 'enter_task_name', type: 'text', name: 'task_name', placeholder: 'Active', required: true, autoFocus: true })
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u4F7F\u7528\u8BF4\u660E'
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { className: 'tr tr-stripe' },
                _react2.default.createElement(
                  'div',
                  { className: 'td1' },
                  _react2.default.createElement(
                    'label',
                    null,
                    '\u57FA\u56E0\u4FE1\u606F:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'label',
                    { htmlFor: 'input_gene_file', className: 'file_input' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u9009\u62E9\u6587\u4EF6'
                    ),
                    _react2.default.createElement('input', { id: 'input_gene_file',
                      type: 'file',
                      name: 'gene_file',
                      required: true, accept: '.txt,.xlsx,.xls,.csv,.vcf',
                      onChange: function onChange(evt) {
                        return _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement(
                      'span',
                      { className: 'prompt' },
                      this.state.input_gene_file
                    )
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u9009\u62E9 Vcf \u6587\u4EF6\uFF0F\xA0.txt .xls .csv\u6587\u4EF6',
                    _react2.default.createElement('br', null),
                    '\uFF08\u6587\u4EF6\u9700\u5305\u542B gene \u4E0E HGVS cDNA\uFF09'
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement(
                  'div',
                  { className: 'td1' },
                  _react2.default.createElement(
                    'label',
                    null,
                    '\u8868\u578B\u4FE1\u606F:',
                    _react2.default.createElement('br', null),
                    '\uFF08\u53EF\u9009\uFF09'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'label',
                    { htmlFor: 'input_phen', className: 'file_input' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u9009\u62E9\u6587\u4EF6'
                    ),
                    _react2.default.createElement('input', {
                      id: 'input_phen',
                      type: 'file',
                      name: 'symptom_file',
                      accept: '.txt',
                      onChange: function onChange(evt) {
                        return _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement(
                      'span',
                      { className: 'prompt' },
                      this.state.input_phen
                    )
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u6587\u5B57\u8F93\u5165'
                  ),
                  _react2.default.createElement('br', null),
                  _react2.default.createElement('textarea', { id: 'myTextArea',
                    name: 'input_text_phenotype',
                    rows: '5',
                    cols: '35',
                    maxLength: '300',
                    placeholder: '\u8868\u578B\u95F4\u4F7F\u7528\u9017\u53F7\u5206\u5272\xA0(\u652F\u6301\u4E2D\u82F1\u6587\u8F93\u5165)' })
                )
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'tb-section' },
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement(
                  'div',
                  { className: 'td1' },
                  _react2.default.createElement(
                    'label',
                    { htmlFor: 'parents_info' },
                    '\u7236\u6BCD\u4FE1\u606F:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u662F\u5426\u63D0\u4F9B\u7236\u4EB2\u57FA\u56E0\u4FE1\u606F:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'a',
                    { 'data-toggle': 'collapse', className: 'switch', href: '#father_detail', onClick: function onClick(evt) {
                        return _this2._handleClick(evt);
                      } },
                    _react2.default.createElement('input', { type: 'checkbox',
                      id: 'check_father',
                      name: 'father_check',
                      checked: this.state.father_check,
                      onChange: function onChange(evt) {
                        _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement('label', { htmlFor: 'check_father', className: 'check slider round' })
                  ),
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u5426/\u662F'
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { id: 'father_detail', className: 'collapse' },
                _react2.default.createElement(
                  'div',
                  { className: 'tr' },
                  _react2.default.createElement('div', { className: 'td1' }),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u662F\u5426\u4E0E\u7236\u4EB2\u6709\u76F8\u540C\u8868\u578B:'
                    )
                  ),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'a',
                      { className: 'switch', onClick: function onClick(evt) {
                          return _this2._handleClick(evt);
                        } },
                      _react2.default.createElement('input', { type: 'checkbox',
                        id: 'check_father_pheno',
                        name: 'father_check_pheno',
                        checked: this.state.father_check_pheno,
                        onChange: function onChange(evt) {
                          _this2._handleChange(evt);
                        } }),
                      _react2.default.createElement('label', { htmlFor: 'check_father_pheno', className: 'check slider round' })
                    ),
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u5426/\u662F'
                    )
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'tr' },
                  _react2.default.createElement('div', { className: 'td1' }),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u4E0A\u4F20\u7236\u4EB2\u57FA\u56E0\u4FE1\u606F:'
                    )
                  ),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'label',
                      { htmlFor: 'father_gene_file', className: 'file_input' },
                      _react2.default.createElement(
                        'span',
                        null,
                        '\u9009\u62E9\u6587\u4EF6'
                      ),
                      _react2.default.createElement('input', {
                        id: 'father_gene_file',
                        type: 'file',
                        name: 'father_gene_file',
                        accept: '.txt,.xlsx,.xls,.csv,.vcf',
                        onChange: function onChange(evt) {
                          return _this2._handleChange(evt);
                        } }),
                      _react2.default.createElement(
                        'span',
                        { className: 'prompt' },
                        this.state.father_gene_file
                      )
                    )
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement('div', { className: 'td1' }),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u662F\u5426\u63D0\u4F9B\u6BCD\u4EB2\u57FA\u56E0\u4FE1\u606F:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'a',
                    { 'data-toggle': 'collapse', className: 'switch', href: '#mother_detail', onClick: function onClick(evt) {
                        return _this2._handleClick(evt);
                      } },
                    _react2.default.createElement('input', { type: 'checkbox',
                      id: 'check_mother',
                      name: 'mother_check',
                      checked: this.state.mother_check,
                      onChange: function onChange(evt) {
                        _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement('label', { htmlFor: 'check_mother', className: 'check slider round' })
                  ),
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u5426/\u662F'
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { id: 'mother_detail', className: 'collapse' },
                _react2.default.createElement(
                  'div',
                  { className: 'tr' },
                  _react2.default.createElement('div', { className: 'td1' }),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u662F\u5426\u4E0E\u6BCD\u4EB2\u6709\u76F8\u540C\u8868\u578B:'
                    )
                  ),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'a',
                      { className: 'switch', onClick: function onClick(evt) {
                          return _this2._handleClick(evt);
                        } },
                      _react2.default.createElement('input', { type: 'checkbox',
                        id: 'check_mother_pheno',
                        name: 'mother_check_pheno',
                        checked: this.state.mother_check_pheno,
                        onChange: function onChange(evt) {
                          _this2._handleChange(evt);
                        } }),
                      _react2.default.createElement('label', { htmlFor: 'check_mother_pheno', className: 'check slider round' })
                    ),
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u5426/\u662F'
                    )
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'tr' },
                  _react2.default.createElement('div', { className: 'td1' }),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'span',
                      null,
                      '\u4E0A\u4F20\u6BCD\u4EB2\u57FA\u56E0\u4FE1\u606F:'
                    )
                  ),
                  _react2.default.createElement(
                    'div',
                    { className: 'td2' },
                    _react2.default.createElement(
                      'label',
                      { htmlFor: 'mother_gene_file', className: 'file_input' },
                      _react2.default.createElement(
                        'span',
                        null,
                        '\u9009\u62E9\u6587\u4EF6'
                      ),
                      _react2.default.createElement('input', {
                        id: 'mother_gene_file',
                        type: 'file',
                        name: 'mother_gene_file',
                        accept: '.txt,.xlsx,.xls,.csv,.vcf',
                        onChange: function onChange(evt) {
                          return _this2._handleChange(evt);
                        } }),
                      _react2.default.createElement(
                        'span',
                        { className: 'prompt' },
                        this.state.mother_gene_file
                      )
                    )
                  )
                )
              )
            ),
            _react2.default.createElement(
              'div',
              { className: 'tb-section' },
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement(
                  'div',
                  { className: 'td1' },
                  _react2.default.createElement(
                    'label',
                    { htmlFor: 'requirement' },
                    '\u62A5\u544A\u8981\u6C42:'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u662F\u5426\u8981\u6C42 incidental findings \u62A5\u544A\uFF1A'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'a',
                    { className: 'switch', onClick: function onClick(evt) {
                        return _this2._handleClick(evt);
                      } },
                    _react2.default.createElement('input', { type: 'checkbox',
                      id: 'check_incidental_findings',
                      name: 'incidental_findings_check',
                      checked: this.state.incidental_findings_check,
                      onChange: function onChange(evt) {
                        _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement('label', { htmlFor: 'check_incidental_findings', className: 'check slider round' })
                  ),
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u5426/\u662F'
                  )
                )
              ),
              _react2.default.createElement(
                'div',
                { className: 'tr' },
                _react2.default.createElement('div', { className: 'td1' }),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u662F\u5426\u8981\u6C42 candidate genes \u62A5\u544A\uFF1A'
                  )
                ),
                _react2.default.createElement(
                  'div',
                  { className: 'td2' },
                  _react2.default.createElement(
                    'a',
                    { className: 'switch', onClick: function onClick(evt) {
                        return _this2._handleClick(evt);
                      } },
                    _react2.default.createElement('input', { type: 'checkbox',
                      id: 'check_candidate_genes',
                      name: 'candidate_genes_check',
                      checked: this.state.candidate_genes_check,
                      onChange: function onChange(evt) {
                        _this2._handleChange(evt);
                      } }),
                    _react2.default.createElement('label', { htmlFor: 'check_candidate_genes', className: 'check slider round' })
                  ),
                  _react2.default.createElement(
                    'span',
                    null,
                    '\u5426/\u662F'
                  )
                )
              )
            )
          ),
          _react2.default.createElement('input', { id: 'task_submit', type: 'submit', value: '\u63D0\u4EA4', onClick: function onClick(evt) {
              return _this2._handleClick(evt);
            } })
        )
      );
    }
  }]);

  return New_task_upload;
}(_react2.default.Component);

New_task_upload.propTypes = {};

New_task_upload.defaultProps = {};

exports.default = New_task_upload;

/***/ }),

/***/ 125:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.Completed_task = exports.Processing_task = undefined;

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Processing_task = function (_React$Component) {
  _inherits(Processing_task, _React$Component);

  function Processing_task(props) {
    _classCallCheck(this, Processing_task);

    return _possibleConstructorReturn(this, (Processing_task.__proto__ || Object.getPrototypeOf(Processing_task)).call(this, props));
  }

  _createClass(Processing_task, [{
    key: "render",
    value: function render() {
      var barStyle = {
        "width": "50%"
      };
      return _react2.default.createElement(
        "div",
        null,
        _react2.default.createElement(
          "p",
          { className: "task-title" },
          "\u4EFB\u52A1\u540D\u79F01\uFF1A80%"
        ),
        _react2.default.createElement(
          "div",
          { className: "progress" },
          _react2.default.createElement(
            "div",
            { className: "progress-bar progress-bar-info", role: "progressbar", "aria-valuenow": "50",
              "aria-valuemin": "0", "aria-valuemax": "100", style: { "width": "50%" } },
            _react2.default.createElement(
              "span",
              { className: "sr-only" },
              "50% Complete"
            )
          )
        ),
        _react2.default.createElement(
          "p",
          { className: "processing-info" },
          " \u6B63\u5728\u5904\u7406\u67D0\u4E2A\u57FA\u56E0 "
        )
      );
    }
  }]);

  return Processing_task;
}(_react2.default.Component);

var Completed_task = function (_React$Component2) {
  _inherits(Completed_task, _React$Component2);

  function Completed_task(props) {
    _classCallCheck(this, Completed_task);

    return _possibleConstructorReturn(this, (Completed_task.__proto__ || Object.getPrototypeOf(Completed_task)).call(this, props));
  }

  _createClass(Completed_task, [{
    key: "render",
    value: function render() {
      return _react2.default.createElement(
        "div",
        { className: "completed_text" },
        _react2.default.createElement(
          "span",
          null,
          "\u4EFB\u52A1\u540D\u79F0"
        ),
        _react2.default.createElement(
          "span",
          null,
          "  \u5B8C\u6210"
        )
      );
    }
  }]);

  return Completed_task;
}(_react2.default.Component);

exports.Processing_task = Processing_task;
exports.Completed_task = Completed_task;

/***/ }),

/***/ 126:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

var _New_task_upload = __webpack_require__(124);

var _New_task_upload2 = _interopRequireDefault(_New_task_upload);

var _New_task_progress = __webpack_require__(123);

var _New_task_progress2 = _interopRequireDefault(_New_task_progress);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var New_task = function (_React$Component) {
  _inherits(New_task, _React$Component);

  function New_task(props) {
    _classCallCheck(this, New_task);

    return _possibleConstructorReturn(this, (New_task.__proto__ || Object.getPrototypeOf(New_task)).call(this, props));
  }

  _createClass(New_task, [{
    key: 'render',
    value: function render() {
      return _react2.default.createElement(
        'div',
        { className: 'new_task' },
        _react2.default.createElement(_New_task_upload2.default, null),
        _react2.default.createElement(_New_task_progress2.default, null),
        _react2.default.createElement(
          'label',
          { className: 'btn btn-primary', htmlFor: 'task_submit' },
          _react2.default.createElement(
            'span',
            null,
            '\u63D0'
          ),
          _react2.default.createElement(
            'span',
            null,
            '\u4EA4'
          )
        )
      );
    }
  }]);

  return New_task;
}(_react2.default.Component);

New_task.propTypes = {};

New_task.defaultProps = {};

exports.default = New_task;

/***/ }),

/***/ 127:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(4);

var _react2 = _interopRequireDefault(_react);

var _reactRouterDom = __webpack_require__(39);

var _base = __webpack_require__(67);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Side_navbar = function (_React$Component) {
  _inherits(Side_navbar, _React$Component);

  function Side_navbar(props) {
    _classCallCheck(this, Side_navbar);

    return _possibleConstructorReturn(this, (Side_navbar.__proto__ || Object.getPrototypeOf(Side_navbar)).call(this, props));
  }

  _createClass(Side_navbar, [{
    key: 'render',
    value: function render() {
      return _react2.default.createElement(
        'nav',
        { className: 'col-sm-2 sidebar' },
        _react2.default.createElement('img', { className: 'bg', src: _base.static_image + "toolbar-bg.png", alt: 'sidebar-bg' }),
        _react2.default.createElement('div', { className: 'bg-filter' }),
        _react2.default.createElement(
          'ul',
          { className: 'nav flex-column' },
          _react2.default.createElement(
            'li',
            { className: 'nav-item' },
            _react2.default.createElement(
              _reactRouterDom.Link,
              { to: '/home/ch/', className: 'nav-link active' },
              _react2.default.createElement('img', { src: _base.static_image + "newtask-icon.png", alt: 'new_task' }),
              _react2.default.createElement(
                'span',
                null,
                '\u65B0\u4EFB\u52A1'
              )
            )
          ),
          _react2.default.createElement(
            'li',
            { className: 'nav-item' },
            _react2.default.createElement(
              _reactRouterDom.Link,
              { to: '/home/ch/task_list', className: 'nav-link' },
              _react2.default.createElement('img', { src: _base.static_image + "tasklist-icon.png", alt: 'task-list' }),
              _react2.default.createElement(
                'span',
                null,
                '\u4EFB\u52A1\u5217\u8868'
              )
            )
          ),
          _react2.default.createElement(
            'li',
            { className: 'nav-item' },
            _react2.default.createElement(
              _reactRouterDom.Link,
              { to: '/home/ch/feedback', className: 'nav-link' },
              _react2.default.createElement('img', { src: _base.static_image + "feedback-icon.png", alt: 'result-review' }),
              _react2.default.createElement(
                'span',
                null,
                '\u7ED3\u679C\u8BC4\u4F30'
              )
            )
          )
        )
      );
    }
  }]);

  return Side_navbar;
}(_react2.default.Component);

Side_navbar.propTypes = {};

Side_navbar.defaultProps = {};

exports.default = Side_navbar;

/***/ }),

/***/ 128:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _redux = __webpack_require__(64);

var _reactRouterRedux = __webpack_require__(66);

var _root_actions = __webpack_require__(121);

var _root_actions2 = _interopRequireDefault(_root_actions);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var root_reducer = function root_reducer() {};

exports.default = root_reducer;

/***/ }),

/***/ 132:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(133)(undefined);
// imports


// module
exports.push([module.i, ".new_task {\n  position: relative;\n  width: 100%;\n  height: 100%;\n  margin-left: 20px;\n  display: flex;\n  flex-flow: row nowrap;\n  justify-content: flex-start;\n  color: #406A8C; }\n  .new_task > label {\n    position: absolute;\n    top: 88%;\n    left: 77%;\n    padding-left: 30px;\n    padding-right: 30px;\n    background-color: #0275d8;\n    border: 0px; }\n    .new_task > label span {\n      padding: 25px 10px; }\n    .new_task > label:hover {\n      background-color: #025fb1; }\n\n.new_task_upload {\n  position: relative;\n  flex-grow: 0;\n  width: 70%;\n  height: 95%;\n  margin-right: 20px;\n  margin-top: 20px;\n  overflow: auto;\n  overflow-x: hidden; }\n  .new_task_upload label {\n    margin-bottom: 0px; }\n  .new_task_upload .file_input {\n    position: relative;\n    z-index: 5;\n    width: 80px;\n    height: 20px;\n    background: #FFFFFF;\n    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.5);\n    border-radius: 8px;\n    margin-bottom: 10px;\n    margin-top: 10px;\n    vertical-align: middle;\n    text-align: center;\n    cursor: pointer; }\n    .new_task_upload .file_input span {\n      position: relative;\n      display: inline-block;\n      font-size: 11px;\n      color: #53BAEC;\n      cursor: pointer; }\n      .new_task_upload .file_input span.prompt {\n        display: block;\n        margin-top: 5px;\n        color: #406A8C;\n        font-size: 10px;\n        cursor: default; }\n    .new_task_upload .file_input input {\n      position: relative;\n      visibility: hidden;\n      width: 0px;\n      height: 0px;\n      z-index: 0; }\n  .new_task_upload textarea {\n    border: 1px solid #e6e6e6; }\n  .new_task_upload #task_submit {\n    display: none; }\n\n.new_task_progress {\n  position: relative;\n  flex-grow: 0;\n  background: #FFFFFF;\n  box-shadow: -3px 2px 2px 0 rgba(119, 151, 178, 0.16);\n  margin-top: 20px;\n  width: 22%;\n  height: 82%;\n  overflow: auto; }\n  .new_task_progress .tb-title {\n    position: relative;\n    width: 100%;\n    padding-top: 0px;\n    padding: 20px; }\n\nbody {\n  overflow: hidden;\n  background-color: #F5F8FA; }\n\nhtml, body, #root, #root > div, .container-fluid, .row {\n  height: 100%; }\n\n.navbar {\n  position: relative;\n  background: #00061D;\n  opacity: 0.85;\n  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.5);\n  margin-bottom: 0;\n  border: 0px;\n  border-radius: 0px;\n  z-index: 10; }\n\n.main_area {\n  position: relative; }\n\n.sidebar {\n  position: relative;\n  z-index: 5;\n  height: 100%;\n  padding-left: 0px;\n  padding-right: 0px;\n  overflow: hidden; }\n  .sidebar .bg {\n    position: absolute;\n    left: 0;\n    top: 0;\n    width: 100%;\n    height: 100%;\n    z-index: 8; }\n  .sidebar .bg-filter {\n    position: absolute;\n    background: linear-gradient(#0b4774, #09385D);\n    left: 0;\n    top: 0;\n    width: 100%;\n    height: 100%;\n    opacity: 0.8;\n    z-index: 10; }\n  .sidebar ul {\n    position: relative;\n    margin-top: 10px;\n    z-index: 20; }\n  .sidebar .nav-item {\n    margin: 10px auto; }\n  .sidebar .nav-link img {\n    display: inline;\n    margin-right: 20px;\n    margin-left: 15%;\n    width: 10%; }\n  .sidebar .nav-link span {\n    color: white;\n    font-size: 16px;\n    font-weight: lighter;\n    letter-spacing: 3px;\n    line-height: 150%;\n    vertical-align: middle; }\n\nmain {\n  position: relative;\n  background-color: #F5F8FA;\n  height: 90%;\n  overflow: scroll; }\n  main::-webkit-scrollbar {\n    display: none; }\n\n.tb-section {\n  margin-bottom: 25px;\n  background-color: white;\n  box-shadow: -3px 2px 2px 0 rgba(119, 151, 178, 0.16); }\n\n.tr {\n  position: relative;\n  width: 100%;\n  display: flex; }\n\n.td1 {\n  position: relative;\n  display: inline;\n  width: 20%;\n  height: 100%;\n  text-align: center;\n  margin: auto 0px;\n  padding-top: 15px;\n  padding-bottom: 15px; }\n\n.td2 {\n  position: relative;\n  display: inline;\n  width: 40%;\n  height: 100%;\n  margin: auto 0px;\n  padding: 10px 0px;\n  font-size: 13px; }\n\n.td3 {\n  position: relative;\n  width: 100%;\n  padding: 15px 20px;\n  font-size: 12px; }\n  .td3 p {\n    margin-bottom: 5px; }\n  .td3 .progress {\n    margin-bottom: 5px;\n    height: 8px; }\n  .td3 .completed_text {\n    padding: 15px 0px; }\n\n.tr-stripe {\n  background-color: #F5F6F7;\n  padding-top: 15px;\n  padding-bottom: 30px; }\n\n.td-stripe {\n  background-color: #F5F6F7; }\n\n.switch {\n  position: relative;\n  display: inline-block;\n  width: 36px;\n  height: 20.4px;\n  margin-right: 5px; }\n  .switch input {\n    visibility: hidden; }\n  .switch .slider {\n    position: absolute;\n    cursor: pointer;\n    top: 0;\n    left: 0;\n    right: 0;\n    bottom: 0;\n    background-color: #ccc;\n    -webkit-transition: .4s;\n    transition: .4s; }\n  .switch .slider:before {\n    position: absolute;\n    content: \"\";\n    height: 15.6px;\n    width: 15.6px;\n    left: 2.4px;\n    bottom: 2.4px;\n    background-color: white;\n    -webkit-transition: .4s;\n    transition: .4s; }\n  .switch input:checked + .slider {\n    background-color: #2196F3; }\n  .switch input:focus + .slider {\n    box-shadow: 0 0 1px #2196F3; }\n  .switch input:checked + .slider:before {\n    -webkit-transform: translateX(15.6px);\n    -ms-transform: translateX(15.6px);\n    transform: translateX(15.6px); }\n  .switch .slider.round {\n    border-radius: 20.4px; }\n  .switch .slider.round:before {\n    border-radius: 50%; }\n", ""]);

// exports


/***/ }),

/***/ 133:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/css-loader/lib/css-base.js'\n    at Error (native)");

/***/ }),

/***/ 274:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/redux-logger/dist/redux-logger.js'\n    at Error (native)");

/***/ }),

/***/ 275:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/redux-thunk/lib/index.js'\n    at Error (native)");

/***/ }),

/***/ 280:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/style-loader/addStyles.js'\n    at Error (native)");

/***/ }),

/***/ 39:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/react-router-dom/es/index.js'\n    at Error (native)");

/***/ }),

/***/ 4:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/react/react.js'\n    at Error (native)");

/***/ }),

/***/ 64:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/redux/es/index.js'\n    at Error (native)");

/***/ }),

/***/ 65:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/history/createBrowserHistory.js'\n    at Error (native)");

/***/ }),

/***/ 66:
/***/ (function(module, exports) {

throw new Error("Module build failed: Error: ENOENT: no such file or directory, open '/Users/xuhuixu/Desktop/geneNova/deepbrain/static/app_ch/node_modules/react-router-redux/es/index.js'\n    at Error (native)");

/***/ }),

/***/ 67:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});
var basic_info = {
  static_image: '../../static/app_ch/files/images/'
};

var static_image = '../../static/app_ch/files/images/';

exports.static_image = static_image;
exports.default = basic_info;

/***/ })

/******/ });