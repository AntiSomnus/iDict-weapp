//index.js
//获取应用实例

const app = getApp();
var WordList = app.globalData.WordList;
var WordDetail = app.globalData.WordDetail;
var WordBrief = app.globalData.WordBrief;
var baseUrl = 'https://ireading.site/'

const {
  $Toast
} = require('../../dist/base/index');
var currentInputWord = '';

function searchWordList(word, that) {
  wx.request({
    url: baseUrl + 'word/list',
    responseType: "arraybuffer",
    data: {
      'word': word,
    },
    header: {
      "Content-Type": "application/text"
    },
    success: function(res) {
      let statusCode = res.statusCode;
      let wordSuggestions;
      if (statusCode === 200) {
        let wordList = WordList.decode(new Uint8Array(res.data));
        if (wordList.wordBriefs.length > 0 && word.toLowerCase() === wordList.wordBriefs[0].wordOut.toLowerCase()) {
          wordSuggestions = null
        } else {
          wordSuggestions = [];
          for (var i = 0; i < Math.min(10, wordList.wordSuggestions.length); i++) {
            wordSuggestions.push(wordList.wordSuggestions[i].wordOut)
          }
        }
        that.setData({
          wordList: wordList.wordBriefs.length > 0 ? wordList.wordBriefs : null,
          isHistoryShow: false,
          wordSuggestions: wordSuggestions,

        })
      } else if (statusCode === 251) {
        //失败 不做操作
      }
    }

  })
}



Page({
  data: {
    wordList: [], //候选单词列表
    viewParam: {}, //关于view的参数字典

  },

  initSearch: function() {
    //用户点击屏幕中央的搜索栏开始搜索
    if (!this.data.isInputExisted) {
      let that = this;
      let animation = wx.createAnimation() //搜索栏上移动画
      let animationFade = wx.createAnimation({ //logo淡出动画
        duration: 200,
        timingFunction: 'linear',
      })
      animationFade.opacity(0).step()
      animation.translate(0, 60 - this.data.viewParam.TotalHeight / 2).step({
        duration: 200
      })
      that.setData({
        animation: animation.export(),
        animationFade: animationFade.export()
      })
      setTimeout(function() {
        that.setData({
          isInitFinished: true
        })
      }, 300)
    }
  },
  clearSearch: function() {
    //用户点击搜索栏的x,清空输入框，列表，标记输入为空
    currentInputWord = '';
    this.setData({
      inputVal: '',
      isHistoryShow: true,
      isInputExisted: false,
      wordList: app.globalData.historyList

    })
  },
  goToKeyWord: function(event) {
    //用户在输入框中回车进入该单词详情页
    wx.navigateTo({
      url: '../word-detail/word-detail?word=' + event.detail.value,
    })
  },
  inputKeyword: function(event) {
    //用户在搜索框中输入，请求list
    currentInputWord = event.detail.value;
    this.setData({
      wordSuggestions: null,
      isInputExisted: event.detail.value ? true : false,
    })
    if (event.detail.value) {
      //如果输入非空
      var that = this;
      setTimeout(function() {
        if (event.detail.value === currentInputWord && currentInputWord != '')
          searchWordList(event.detail.value, that)
      }, 300)
    } else { //输入为空，清空List
      this.setData({
        wordList: app.globalData.historyList,
        isHistoryShow: true,
      })
    }


  },

  wordClick: function(e) {
    //点击List中的单词，跳转到详情
    var currentWord = e.currentTarget.dataset.word
    wx.navigateTo({
      url: '../word-detail/word-detail?word=' + currentWord +'&isHistoryShow='+this.data.isHistoryShow
    })

  },

  articleClick: function() {
    //点击文章
    wx.navigateTo({
      url: '../article-detail/article-detail'
    })
  },
  onReady:function(){
    this.setData({
      wordList:app.globalData.historyList,
      isHistoryShow: app.globalData.historyList.length>0
    })
  },
  onLoad: function() {
    var that = this;
    var query = wx.createSelectorQuery();
    var param = that.data.viewParam;
    //测量搜索栏和tab的高度
    query.select('#fixed-top').boundingClientRect()
    query.exec(function(res) {
      param.topHeight = res[0].height;
      that.setData({
        viewParam: param
      });
    })
    //测量用户屏幕页面高度
    wx.getSystemInfo({
      success: function(res) {
        param.TotalHeight = res.windowHeight;
        that.setData({
          viewParam: param
        });
      }
    })
    
  },

  onReachBottom: function() {
    /*
    var that=this;
    var l = that.data.tags.length;
    var l2=[l+1,l+2,l+3,l+4,l+5];
    that.setData({
      tags: that.data.tags.concat(l2)
    });*/
  },
  wordSuggestionChange: function(e) {
    let word = this.data.wordSuggestions[e.detail.value]
    this.setData({
      inputVal: word
    })
    searchWordList(word, this)

  },
  wordSuggestionClick: function(e) {
    let word = e.currentTarget.dataset.word
    this.setData({
      inputVal: word
    })
    searchWordList(word, this)
  },
  betaClicked: function() {
    $Toast({
      content: '智能拼写检查，此功能仍处于测试阶段',
      type: 'warning'
    });
  },
  clearHistory: function() {
    app.clearHistory()
    this.setData({
      wordList: [],
      isHistoryShow: false
    })

  },
  onPullDownRefresh: function() {
    wx.stopPullDownRefresh();

    /*
     // 显示顶部刷新图标
     wx.showNavigationBarLoading();
     var that = this;
     wx.request({
       url: 'http://47.106.165.55:5000/',
       data: {
         'word': 'happy',
         'json': true,
         'stem': true
       },
       header: {
         "Content-Type": "application/text"
       },
       success: function (res) {
         wx.hideNavigationBarLoading();
         // 停止下拉动作
         wx.stopPullDownRefresh();
       }    //参数为键值对字符串

     })*/
  }

})