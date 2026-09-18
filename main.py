# -*- coding: utf-8 -*-
"""
GI/GL 食物卡牌分类游戏 —— Android (Kivy) 版主程序
本地测试：python main.py
打包：buildozer android debug
"""
import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as hexc

import card_data as cd
import game_logic as gl

# ---------------- 中文字体注册 ----------------
_font_loaded = False
for _path in [
    "NotoSansSC-Regular.otf",     # 打包进 APK 的字体（Android）
    "NotoSansCJK-Regular.ttc",
    "msyh.ttc",                    # Windows 微软雅黑（本地测试）
    "simhei.ttf",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]:
    if os.path.exists(_path):
        try:
            LabelBase.register(name="CN", fn_regular=_path)
            _font_loaded = True
            break
        except Exception:
            continue


def CN_F(size="14sp"):
    if _font_loaded:
        return "CN"
    return "Roboto"  # 兜底（中文会显示方块，仅极少数环境）


# ---------------- 颜色 ----------------
COL = {
    "bg": (0.965, 0.945, 0.906, 1),
    "header": (0.184, 0.322, 0.200, 1),
    "dialogue": (1.0, 0.973, 0.882, 1),
    "dialogue_fg": (0.365, 0.247, 0.216, 1),
    "box": (1, 1, 1, 1),
    "box_border": (0.54, 0.54, 0.54, 1),
    "box_title": (0.91, 0.88, 0.80, 1),
    "card": (1.0, 0.984, 0.902, 1),
    "card_border": (0.79, 0.64, 0.15, 1),
    "card_ok": (0.835, 0.929, 0.851, 1),
    "card_ok_border": (0.18, 0.545, 0.341, 1),
    "card_wrong": (0.973, 0.843, 0.855, 1),
    "card_wrong_border": (0.753, 0.224, 0.169, 1),
    "btn": (0.91, 0.88, 0.80, 1),
    "btn_primary": (0.184, 0.322, 0.200, 1),
    "text": (0.2, 0.2, 0.2, 1),
    "text_light": (1, 1, 1, 1),
}


class CardButton(Button):
    """可拖拽卡牌。"""
    def __init__(self, game, card, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None)
        self.game = game
        self.card = card
        self.home_pos = (0, 0)
        self.current_box = None     # 所在框标签，None=卡牌池
        self.locked = False
        self._grab_off = (0, 0)
        self._down_pos = (0, 0)
        self.background_normal = ""
        self.background_color = COL["card"]
        self.color = COL["text"]
        self.border = (1, 1, 1, 1)
        self._refresh()

    def _refresh(self):
        if self.locked:
            self.background_color = COL["card_ok"]
        else:
            self.background_color = COL["card"]

    def on_touch_down(self, touch):
        if self.locked:
            return False
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._grab_off = (self.center_x - touch.x, self.center_y - touch.y)
            self._down_pos = (touch.x, touch.y)
            self.game.lift_card(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.center_x = touch.x + self._grab_off[0]
            self.center_y = touch.y + self._grab_off[1]
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            moved = (abs(touch.x - self._down_pos[0]) > dp(6) or
                     abs(touch.y - self._down_pos[1]) > dp(6))
            if moved:
                self.game.drop_card(self)
            else:
                self.game.show_detail(self.card)
            return True
        return super().on_touch_up(touch)


class BoxArea(Widget):
    """投放框（视觉区域 + 标题）。"""
    def __init__(self, game, label, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None)
        self.game = game
        self.label = label
        with self.canvas:
            Color(*COL["box_border"])
            self.rect = Rectangle(pos=self.pos, size=self.size)
            Color(*COL["box"])
            self.inner = Rectangle(pos=(self.x + dp(2), self.y + dp(2)),
                                   size=(self.width - dp(4), self.height - dp(4)))
            Color(*COL["box_title"])
            self.title_rect = Rectangle(pos=(self.x + dp(2), self.y + self.height - dp(30)),
                                        size=(self.width - dp(4), dp(28)))
        self.bind(pos=self._redraw, size=self._redraw)
        # 标题文字
        self.title_lbl = Label(text=label, font_name=CN_F("15sp"), font_size="15sp",
                               color=COL["text"], halign="center", valign="middle")
        self.title_lbl.bind(size=lambda *a: setattr(self.title_lbl, "text_size", self.title_lbl.size))
        self.add_widget(self.title_lbl)

    def _redraw(self, *a):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.inner.pos = (self.x + dp(2), self.y + dp(2))
        self.inner.size = (self.width - dp(4), self.height - dp(4))
        self.title_rect.pos = (self.x + dp(2), self.y + self.height - dp(30))
        self.title_rect.size = (self.width - dp(4), dp(28))
        self.title_lbl.pos = (self.x + dp(4), self.y + self.height - dp(30))
        self.title_lbl.size = (self.width - dp(8), dp(28))

    def contains(self, cx, cy):
        return self.x <= cx <= self.x + self.width and self.y <= cy <= self.y + self.height


class GameScreen(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.score = 0
        self.level_idx = 1
        self.max_unlocked = 1
        self.wrong_records = []
        self.current_level = None
        self.cards = []
        self.card_widgets = {}
        self.boxes = []          # [(label, BoxArea)]
        self.card_home = {}
        self.card_box = {}
        self.card_locked = {}
        self.dialogue_lbl = None
        Window.bind(size=self._on_resize)
        Clock.schedule_once(lambda dt: self.show_scene(), 0)

    def _on_resize(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COL["bg"])
            Rectangle(pos=self.pos, size=self.size)

    # ---------------- 场景分发 ----------------
    def show_scene(self):
        self.clear_widgets()
        self.card_widgets = {}
        self.boxes = []
        self.card_home = {}
        self.card_box = {}
        self.card_locked = {}
        self.cards = []
        lv = cd.LEVELS[self.level_idx]
        if lv["type"] == "intro":
            self._show_intro(lv)
        elif lv["type"] in ("gi3", "gl3", "dual4"):
            self._show_level(lv)
        elif lv["type"] == "quiz":
            self._show_quiz(lv)
        elif lv["type"] == "result":
            self._show_result()

    def _header(self, title):
        h = BoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(46),
                      pos=(0, self.height - dp(46)))
        with h.canvas.before:
            Color(*COL["header"])
            Rectangle(pos=h.pos, size=h.size)
        h.bind(pos=lambda w, *a: self._redraw_header(w),
               size=lambda w, *a: self._redraw_header(w))
        h.title_lbl = Label(text=title, font_name=CN_F("17sp"), font_size="17sp",
                            color=COL["text_light"], halign="left", valign="middle")
        h.title_lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        h.score_lbl = Label(text=f"积分：{self.score}", font_name=CN_F("15sp"), font_size="15sp",
                            color=COL["text_light"], halign="right", valign="middle")
        h.score_lbl.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        h.add_widget(h.title_lbl)
        h.add_widget(h.score_lbl)
        self.add_widget(h)
        return h

    def _redraw_header(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*COL["header"])
            Rectangle(pos=w.pos, size=w.size)
        w.title_lbl.size = (w.width * 0.6, w.height)
        w.score_lbl.size = (w.width * 0.4, w.height)
        w.title_lbl.pos = (dp(8), 0)
        w.score_lbl.pos = (w.width * 0.6, 0)

    def _dialogue(self, text):
        d = Label(text=text, font_name=CN_F("14sp"), font_size="14sp",
                  color=COL["dialogue_fg"], halign="left", valign="top",
                  text_size=(self.width - dp(24), None), size_hint=(None, None))
        d.bind(texture_size=lambda w, *a: setattr(w, "size", w.texture_size))
        d.size = (self.width - dp(24), dp(20))
        with d.canvas.before:
            Color(*COL["dialogue"])
            Rectangle(pos=d.pos, size=d.size)
        d.bind(pos=lambda w, *a: self._redraw_dialogue(w),
               size=lambda w, *a: self._redraw_dialogue(w))
        self.add_widget(d)
        self.dialogue_lbl = d
        return d

    def _redraw_dialogue(self, w):
        w.canvas.before.clear()
        with w.canvas.before:
            Color(*COL["dialogue"])
            Rectangle(pos=w.pos, size=w.size)

    # ---------------- 场景0：知识点 ----------------
    def _show_intro(self, lv):
        self._header("GI/GL 食物卡牌分类小游戏")
        text = "\n".join(lv["content"])
        lab = Label(text=text, font_name=CN_F("14sp"), font_size="14sp",
                    color=COL["text"], halign="center", valign="middle",
                    text_size=(self.width - dp(40), None), size_hint=(None, None))
        lab.size = (self.width - dp(40), self.height - dp(140))
        lab.pos = (dp(20), dp(70))
        self.add_widget(lab)
        self._button("开始闯关", self._start_game, primary=True,
                     pos=(self.width / 2 - dp(90), dp(20)), size=(dp(180), dp(48)))

    def _start_game(self):
        self.level_idx = 1
        self.max_unlocked = max(self.max_unlocked, 1)
        self.show_scene()

    # ---------------- 闯关场景 ----------------
    def _show_level(self, lv):
        self.current_level = lv
        self._header(f"{lv['name']}  {lv['difficulty']}")
        d = self._dialogue(f"小站（营养师）：{lv['dialogue']}")
        d.pos = (dp(12), self.height - dp(108))
        d.size = (self.width - dp(24), dp(54))

        self.cards = gl.draw_cards(lv)
        for c in self.cards:
            self.card_box[c["name"]] = None
            self.card_locked[c["name"]] = False

        labels = gl.get_box_labels(lv["type"])
        self._build_boxes(labels)
        self._build_cards()
        self._build_level_buttons()

    def _build_boxes(self, labels):
        n = len(labels)
        top = self.height - dp(230)
        gap = dp(8)
        margin = dp(10)
        bw = (self.width - margin * 2 - gap * (n - 1)) / n
        for i, lab in enumerate(labels):
            bx = margin + i * (bw + gap)
            b = BoxArea(self, lab, pos=(bx, top), size=(bw, dp(150)))
            self.add_widget(b)
            self.boxes.append((lab, b))

    def _build_cards(self):
        pool_top = self.height - dp(230) - dp(175)
        margin = dp(10)
        cw = (self.width - margin * 2) / 4
        ch = dp(60)
        for i, c in enumerate(self.cards):
            col = i % 4
            row = i // 4
            x = margin + col * cw
            y = pool_top - row * (ch + dp(6))
            self.card_home[c["name"]] = (x, y)
            w = CardButton(self, c, text=self._card_text(c),
                           font_name=CN_F("11sp"), font_size="11sp",
                           pos=(x, y), size=(cw - dp(6), ch))
            self.add_widget(w)
            self.card_widgets[c["name"]] = w

    def _card_text(self, c):
        lv = self.current_level
        if lv["type"] == "gl3":
            return f"{c['name']}\nGL {c['gl']}"
        if lv["type"] == "dual4":
            return c["name"]
        return f"{c['name']}\nGI {c['gi']}"

    def _build_level_buttons(self):
        bw = (self.width - dp(40)) / 3
        y = dp(10)
        self._button("提示(-10)", self._on_hint, pos=(dp(10), y), size=(bw, dp(44)))
        self._button("提交核对", self._on_submit, primary=True,
                     pos=(dp(10) + bw + dp(10), y), size=(bw, dp(44)))
        self._button("重玩本关", self._on_replay, pos=(dp(10) + (bw + dp(10)) * 2, y),
                     size=(bw, dp(44)))

    def _button(self, text, cmd, primary=False, pos=(0, 0), size=(0, 0)):
        b = Button(text=text, font_name=CN_F("15sp"), font_size="15sp",
                   background_normal="", background_down="",
                   background_color=COL["btn_primary"] if primary else COL["btn"],
                   color=COL["text_light"] if primary else COL["text"],
                   pos=pos, size=size, size_hint=(None, None))
        b.bind(on_release=lambda *a: cmd())
        self.add_widget(b)
        return b

    # ---------------- 拖拽辅助 ----------------
    def lift_card(self, w):
        self.remove_widget(w)
        self.add_widget(w)

    def drop_card(self, w):
        cx, cy = w.center
        for lab, box in self.boxes:
            if box.contains(cx, cy):
                self._place_card(w, lab)
                return
        self._return_card(w)

    def _place_card(self, w, box_label):
        w.current_box = box_label
        self.card_box[w.card["name"]] = box_label
        self._relayout_box(box_label)

    def _return_card(self, w):
        w.current_box = None
        self.card_box[w.card["name"]] = None
        hx, hy = self.card_home[w.card["name"]]
        w.pos = (hx, hy)

    def _relayout_box(self, box_label):
        box = None
        for lab, b in self.boxes:
            if lab == box_label:
                box = b
                break
        if box is None:
            return
        inside = [c for c in self.cards
                  if self.card_box[c["name"]] == box_label and not self.card_locked[c["name"]]]
        locked = [c for c in self.cards
                  if self.card_box[c["name"]] == box_label and self.card_locked[c["name"]]]
        all_in = inside + locked
        cw = dp(50)
        ch = dp(52)
        per_row = max(1, int(box.width // (cw + dp(4))))
        for i, c in enumerate(all_in):
            row = i // per_row
            col = i % per_row
            x = box.x + dp(4) + col * (cw + dp(4))
            y = box.y + dp(4) + row * (ch + dp(4))
            self.card_widgets[c["name"]].pos = (x, y)
            self.card_widgets[c["name"]].size = (cw, ch)

    # ---------------- 详情弹窗 ----------------
    def show_detail(self, c):
        lv = self.current_level
        info = f"名称：{c['name']}\n品类：{c['category']}\nGI：{c['gi']}   GL：{c['gl']}"
        if lv and lv["type"] == "dual4":
            info += f"\n双维度：{c['gi_level']} + {c['gl_level']}"
        info += f"\n\n控糖提示：\n{c['tip']}"
        self._popup(c["name"], info)

    def _popup(self, title, text):
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        lab = Label(text=text, font_name=CN_F("14sp"), font_size="14sp",
                    halign="left", valign="top")
        lab.bind(size=lambda w, *a: setattr(w, "text_size", w.size))
        btn = Button(text="关闭", font_name=CN_F("15sp"), size_hint_y=None, height=dp(44),
                     background_color=COL["btn_primary"])
        content.add_widget(lab)
        content.add_widget(btn)
        pop = Popup(title=title, content=content, size_hint=(0.85, 0.55),
                    title_font=CN_F("15sp"))
        btn.bind(on_release=pop.dismiss)
        pop.open()

    # ---------------- 提交核对 ----------------
    def _on_submit(self):
        lv = self.current_level
        unfilled = [c["name"] for c in self.cards if self.card_box[c["name"]] is None]
        if unfilled:
            self._popup("提示", f"还有 {len(unfilled)} 张卡牌未分类，请全部放置后再提交。")
            return
        correct = 0
        first_wrong = None
        for c in self.cards:
            box = self.card_box[c["name"]]
            ans = gl.get_answer(c, lv["type"])
            w = self.card_widgets[c["name"]]
            if box == ans:
                self.card_locked[c["name"]] = True
                w.locked = True
                w.background_color = COL["card_ok"]
                correct += 1
            else:
                if first_wrong is None:
                    first_wrong = c
                self.wrong_records.append({"name": c["name"], "wrong": box, "right": ans})
                self._return_card(w)
                w.background_color = COL["card_wrong"]
        for lab, box in self.boxes:
            self._relayout_box(lab)
        if first_wrong is not None:
            ans = gl.get_answer(first_wrong, lv["type"])
            self._set_dialogue(f"复盘：『{first_wrong['name']}』放错了（应为【{ans}】）。{lv['review'].get(ans, '')}")
        if correct >= lv["pass_score"]:
            self.score += lv["reward"]
            self.max_unlocked = max(self.max_unlocked, lv["id"] + 1)
            self._offer_next(lv, correct)
        else:
            self._popup("未通过", f"正确 {correct}/{len(self.cards)}，需 ≥{lv['pass_score']} 张，可重玩本关。")

    def _set_dialogue(self, text):
        if self.dialogue_lbl is not None:
            self.dialogue_lbl.text = text
        else:
            self._popup("复盘", text)

    def _offer_next(self, lv, correct):
        self._popup("通关", f"正确 {correct}/{len(self.cards)} 张，通过！积分 +{lv['reward']}")
        # 底部按钮区刷新为 下一关
        for w in list(self.children):
            if isinstance(w, Button) and w.text in ("提交核对", "提示(-10)", "重玩本关"):
                self.remove_widget(w)
        bw = (self.width - dp(40)) / 2
        y = dp(10)
        self._button("重玩本关", self._on_replay, pos=(dp(10), y), size=(bw, dp(44)))
        nxt = "下一关" if lv["id"] < 6 else "结业问答"
        nxt_idx = lv["id"] + 1 if lv["id"] < 6 else 7
        self._button(nxt, lambda: self._goto(nxt_idx), primary=True,
                     pos=(dp(10) + bw + dp(10), y), size=(bw, dp(44)))

    def _on_replay(self):
        self.show_scene()

    def _goto(self, idx):
        self.level_idx = idx
        self.show_scene()

    # ---------------- 提示 ----------------
    def _on_hint(self):
        if self.score < cd.HINT_COST:
            self._popup("提示", f"积分不足，提示需要 {cd.HINT_COST} 积分。")
            return
        unfilled = [c for c in self.cards if self.card_box[c["name"]] is None and not self.card_locked[c["name"]]]
        if not unfilled:
            self._popup("提示", "所有卡牌都已放置，提交核对吧！")
            return
        self.score -= cd.HINT_COST
        c = unfilled[0]
        self._set_dialogue(f"提示：看看『{c['name']}』，属于【{c['category']}】。{c['tip']}")
        self._update_score()

    def _update_score(self):
        for w in self.children:
            if hasattr(w, "score_lbl"):
                w.score_lbl.text = f"积分：{self.score}"

    # ---------------- 结业问答 ----------------
    def _show_quiz(self, lv):
        self._header("结业综合问答")
        self._dialogue("小站：最后一道综合题，检验你是否真正掌握 GI+GL。")
        q = Label(text=lv["question"], font_name=CN_F("16sp"), font_size="16sp",
                  color=COL["text"], halign="left", valign="top",
                  text_size=(self.width - dp(40), None), size_hint=(None, None))
        q.size = (self.width - dp(40), dp(60))
        q.pos = (dp(20), self.height - dp(180))
        self.add_widget(q)
        for i, opt in enumerate(lv["options"]):
            y = self.height - dp(260) - i * dp(70)
            b = Button(text=opt, font_name=CN_F("14sp"), font_size="14sp",
                       background_normal="", background_color=COL["card"],
                       color=COL["text"], halign="left", valign="middle",
                       pos=(dp(20), y), size=(self.width - dp(40), dp(60)),
                       size_hint=(None, None))
            b.bind(on_release=lambda *a, i=i: self._answer_quiz(i))
            self.add_widget(b)

    def _answer_quiz(self, i):
        lv = cd.LEVELS[7]
        if i == lv["correct"]:
            self.score += 10
            msg = lv["explain"]["1"]
        else:
            self.score -= 10
            msg = lv["explain"][str(i)]
        self._popup("作答", msg)
        self.level_idx = 8
        self.show_scene()

    # ---------------- 全局结算 ----------------
    def _show_result(self):
        self._header("全局结算")
        grade = ""
        for th, txt in cd.RESULT_THRESHOLDS:
            if self.score >= th:
                grade = txt
                break
        lab = Label(text=f"总分：{self.score} 分\n\n{grade}",
                    font_name=CN_F("18sp"), font_size="18sp", color=COL["text"],
                    halign="center", valign="middle", text_size=(self.width - dp(60), None),
                    size_hint=(None, None))
        lab.size = (self.width - dp(60), self.height - dp(200))
        lab.pos = (dp(30), dp(80))
        self.add_widget(lab)
        if self.wrong_records:
            seen = {}
            for r in self.wrong_records:
                seen[r["name"]] = r
            lines = "\n".join(f"· {n}：误判【{r['wrong']}】，应为【{r['right']}】" for n, r in seen.items())
        else:
            lines = "无错题，完美通关！"
        wlab = Label(text="错题回顾：\n" + lines, font_name=CN_F("12sp"), font_size="12sp",
                     color=(0.5, 0.37, 0.25, 1), halign="left", valign="top",
                     text_size=(self.width - dp(60), None), size_hint=(None, None))
        wlab.size = (self.width - dp(60), dp(120))
        wlab.pos = (dp(30), dp(60))
        self.add_widget(wlab)
        bw = (self.width - dp(40)) / 2
        self._button("重玩全部", self._restart_all, pos=(dp(10), dp(10)), size=(bw, dp(44)))
        self._button("返回首页", self._back_home, primary=True,
                     pos=(dp(10) + bw + dp(10), dp(10)), size=(bw, dp(44)))

    def _restart_all(self):
        self.score = 0
        self.wrong_records = []
        self.max_unlocked = 1
        self.level_idx = 1
        self.show_scene()

    def _back_home(self):
        self.level_idx = 0
        self.show_scene()


class GIGLApp(App):
    def build(self):
        self.title = "GI/GL 食物卡牌分类"
        return GameScreen()


if __name__ == "__main__":
    GIGLApp().run()
