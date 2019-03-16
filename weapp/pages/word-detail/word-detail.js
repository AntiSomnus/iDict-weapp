//获取应用实例
const app = getApp()
var WordList = app.globalData.WordList;
var WordDetail = app.globalData.WordDetail;
var WordBrief = app.globalData.WordBrief;
const myaudio = app.globalData.audio;

var baseUrl = 'https://ireading.site/'

const sourceDict = {
  0: "牛津高阶英汉双解词典",
  1: "剑桥高阶英汉双解词典",
  2: "朗文当代高级英语辞典",
  3: "柯林斯英汉双解大词典 ",
  4: "金山词霸在线词典"
}

const {
  $Toast
} = require('../../dist/base/index');

var feedback = {};
var defaultFeedbackWord = '';
var wordNotCollected = false;

function replaceAll(str, find, replace) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function modifiedStrToList(modifiedStr) {
  return modifiedStr.split(/(&nbsp;)|([a-zA-Z][a-zA-Z-']*)/g).filter(function(n) {
    return n
  });

}

function separate(str) {
  return str
    .split(/([a-zA-Z][a-zA-Z-']*[\.,?!;\s]*)/g)
    .filter(n => n)
    .map(s => {
      const r = /[\.,?!;\s]+$/.exec(s)
      if (r)
        return [s.slice(0, r.index), s.slice(r.index).replace(' ', '&nbsp;')]
      return s
    });
}


Page({
  data: {
    detailedWord: null,
    sentenceOnline: null,
    maxSentNumber: [10, 10, 10, 10, 10],
    feedbackSectionArray: [
      "内容有误",
      "尚未收录",
      "其他问题",
      "产品建议",
    ],
    feedbackSectionIndex: 0,
    sourceIndex: 0,
    windowHeight: app.globalData.windowHeight
  },


  onLoad: function(param) {
    var that = this;
    wx.request({
      url: baseUrl + 'word/detail',
      responseType: "arraybuffer",
      data: {
        'word': param.word,
      },
      header: {
        "Content-Type": "application/text"
      },
      success: function(res) {
        if (res.statusCode === 200) {
          const wordDetail = WordDetail.decode(new Uint8Array(res.data))
          const sourceArray = wordDetail.sentenceLists.map(s => sourceDict[s.source])

          defaultFeedbackWord = wordDetail.wordBrief.wordOut
          that.setData({
            isLoadingFinished: true,
            detailedWord: wordDetail,
            sourceArray: sourceArray
          })
          app.updateHistory(wordDetail.wordBrief, param.isHistoryShow)
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
    wx.request({
      url: baseUrl + "word/example",
      data: {
        'word': param.word,
      },
      header: {
        "Content-Type": "application/text"
      },
      success: function(res) {
        if (res.statusCode === 200) {
          if (res.data.result.sentences) {
            let each, engStr, origSent
            let engOnlineSents = []
            for (var i = 0; i < res.data.result.sentences.length; i++) {
              each = res.data.result.sentences[i]
              origSent = each.sentence.replace(new RegExp("[\u2019‘’]", "gm"), "'").replace(new RegExp("[“”]", "gm"), '"')

              engOnlineSents.push({
                origSent: origSent,
                source: each.volume.corpus.name,
                datePublished: new Date(each.volume.datePublished).toLocaleDateString(),
                url: each.volume.locator
              });
            }
            that.setData({
              sentenceOnline: engOnlineSents
            })
          }
        }

      }
    })

  },
  feedbackSectionChange: function(e) {
    this.setData({
      feedbackSectionIndex: e.detail.value
    })
  },
  sourceChange: function(e) {
    this.setData({
      sourceIndex: e.detail.value
    })
  },
  audioClicked: function(e) {
    myaudio.src = e.target.dataset.src
    myaudio.play();
  },
  wordClickedInWordDetail: function(e) {
    var data = e.detail;
    var that = this;
    var word = data.word;
    if (word !== undefined && /^([a-zA-Z][a-zA-z-']*)$/.test(word) && word) {
      var currentClickedWord = {};
      currentClickedWord.indexSent = data.indexSent;
      currentClickedWord.indexWord = data.indexWord;
      currentClickedWord.section = data.section;
      currentClickedWord.word = word;
      this.setData({
        current: data,
      });
      wx.request({
        url: baseUrl + 'word/brief',
        responseType: "arraybuffer",
        data: {
          'word': word,
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
            currentClickedWordInfo.wordOut = word;
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
    } else {
      this.setData({
        isShowWordInDetail: false,
        current: {},
      });
    }


  },
  loadMoreSent: function() {
    let ar = this.data.maxSentNumber;
    ar[this.data.sourceIndex] += 10;
    this.setData({
      maxSentNumber: ar
    })
  },
  detailOutClicked: function() {
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
  longTapToWordDetail: function() {
    let popupWord = this.data.currentClickedWordInfo.wordOut;
    let detailedWord = this.data.detailedWord.wordBrief.wordOut;
    if (popupWord !== detailedWord)
      wx.navigateTo({
        url: '../word-detail/word-detail?word=' + this.data.currentClickedWordInfo.wordOut,
      })
  },
  onReachBottom: function() {
    let ar = this.data.maxSentNumber;
    ar[this.data.sourceIndex] += 10;
    this.setData({
      maxSentNumber: ar
    }, 100)
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

  }

})