// pages/chn-detail.js
const app = getApp()
const baseUrl = 'https://ireading.site/'

const ChnDetail = app.globalData.ChnDetail;
const WordBrief = app.globalData.WordBrief;

const myaudio = app.globalData.audio;

var feedback = {};
var defaultFeedbackWord = '';
var wordNotCollected = false;
const {
  $Toast
} = require('../../dist/base/index');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    windowHeight: app.globalData.windowHeight,
    feedbackSectionArray: [
      "内容有误",
      "尚未收录",
      "其他问题",
      "产品建议",
    ],
    feedbackSectionIndex: 0,

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(param) {
    let that = this;
    wx.request({
      url: baseUrl + 'chn/detail',
      responseType: "arraybuffer",
      data: {
        'chn': param.word,
      },
      header: {
        "Content-Type": "application/text"
      },
      success: function(res) {
        if (res.statusCode === 200) {
          const chnDetail = ChnDetail.decode(new Uint8Array(res.data))
          that.setData({
            chnDetail: chnDetail,
            isLoadingFinished: true,
          })
          defaultFeedbackWord = chnDetail.chn
          app.updateHistory({
            wordOut: chnDetail.chn,
            chnDefinitions: [{
              meaning: chnDetail.meanings[0].words.join('; ')
            }]
          }, param.isHistoryShow)

        } else { //error
          defaultFeedbackWord = param.word
          wordNotCollected = true;
          that.setData({
            isLoadingFinished: true,
            errorInfo: {
              word: param.word,
              msg: "抱歉，暂无该单词释义"
            }
          })
        }

      }
    });
  },

  wordClickedInDetail(e) {
    const data = e.detail
    const word = data.word;
    if (word !== undefined && /^([a-zA-Z][a-zA-z-']*)$/.test(word)) {
      let that = this;
      this.setData({
        current: data
      })
      wx.request({
        url: baseUrl + 'word/brief',
        responseType: "arraybuffer",
        data: {
          'word': data.word,
        },
        header: {
          "Content-Type": "application/text"
        },
        responseType: "arraybuffer",

        success: function(res) {
          var currentClickedWordInfo = {}
          if (res.statusCode === 200) {
            currentClickedWordInfo = WordBrief.decode(new Uint8Array(res.data));
          } else {
            currentClickedWordInfo.notCollected = true;
            currentClickedWordInfo.wordOut = data.word;
            currentClickedWordInfo.chnDefinitions = []
            currentClickedWordInfo.chnDefinitions[0] = {}
            currentClickedWordInfo.chnDefinitions[0].meaning = "暂未被收录"
          }
          that.setData({
            isShowWordInDetail: true,
            currentClickedWordInfo: currentClickedWordInfo
          })
        }
      })
    } else this.setData({
      isShowWordInDetail: false,
      current: {},
    });
  },
  detailOutClicked() {
    this.setData({
      isShowWordInDetail: false,
      current: {},
    });
  },
  feedbackOutClicked: function(e) {
    if (e.target.id === 'overlay')
      this.setData({
        isFeedbackShow: false,
      });
  },
  feedbackClicked: function(e) {
    feedback.word = e.target.dataset.type ? this.data.currentClickedWordInfo.wordOut : defaultFeedbackWord;
    feedback.content = '';
    this.setData({
      feedbackWord: feedback.word,
      feedbackSectionIndex: e.target.dataset.type || wordNotCollected ? 1 : 0,
      isFeedbackShow: true
    })
  },
  inputFeedbackWord: function(e) {
    feedback.word = e.detail.value

  },
  feedbackContentInput: function(e) {
    feedback.content = e.detail.value
  },
  feedbackSubmit: function() {
    var that = this;
    wx.request({
      url: baseUrl + 'support/',
      method: "POST",
      data: {
        'type': this.data.feedbackSectionIndex,
        'details': feedback.word + '\r\n' + feedback.content
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        $Toast({
          content: '提交成功',
          type: 'success'
        });
        that.setData({
          isFeedbackShow: false,
          feedbackContent: '',
        })
      },
      fail: function(res) {
        $Toast({
          content: '提交失败',
          type: 'error'
        });
      }
    })

  },
  longTapToWordDetail: function() {
    wx.navigateTo({
      url: '../word-detail/word-detail?word=' + this.data.currentClickedWordInfo.wordOut,
    })
  },
  audioClicked: function(e) {
    myaudio.src = e.target.dataset.src
    myaudio.play();
  },

})