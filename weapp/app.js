//app.js
var protobuf = require('./weichatPb/protobuf.js');
var wordConfig = require('./wordProto.js');
var wordRoot = protobuf.Root.fromJSON(wordConfig);
var WordList = wordRoot.lookupType("WordList");
var WordDetail = wordRoot.lookupType("WordDetail");
var WordBrief = wordRoot.lookupType("WordBrief");

App({

  globalData: {
    userInfo: null,
    WordList: WordList,
    WordBrief: WordBrief,
    WordDetail: WordDetail,
  },
  updateHistory: function(wordBrief,isClickedFromHistory) {
    console.log(isClickedFromHistory)
    let historyList = this.globalData.historyList;
    for (let i = 0; i < historyList.length; i++) {
      if (historyList[i].wordOut === wordBrief.wordOut) {
        //如果该单词已经存在于历史记录中，则删去该单词
        historyList.splice(i, 1);
        break;
      }
    }
    historyList.unshift(wordBrief);
    wx.setStorage({
      key: 'historyList',
      data: historyList,
    })
    this.globalData.historyList = historyList;
    if (isClickedFromHistory==='true')
      getCurrentPages()[0].setData({
        wordList: historyList
    })

  },
  clearHistory: function() {
    this.globalData.historyList = []
    wx.clearStorage()

  },
  onLaunch: function() {
    //计算屏幕高度
    var that = this;
    wx.getSystemInfo({
      success: function(res) {
        that.globalData.windowHeight = res.windowHeight;
      }
    })
    wx.getStorage({
      key: 'historyList',
      success: function(res) {
        that.globalData.historyList = res.data;
      },
      fail: function() {
        that.globalData.historyList = [];

      }
    })
  }



})