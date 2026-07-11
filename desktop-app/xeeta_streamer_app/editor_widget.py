"""Editor de mapeamento de teclas (spec feature-button-mapping).

Um `main_window.py` PyQt6 simplificado — cada tecla fisica vira uma linha
com modificadores + a tecla em si, ao inves do editor drag-and-drop completo
do MacroTouch (referencia arquitetural, nao copiada; ver README do repo).
Suficiente para atribuir uma acao a cada tecla sem editar JSON na mao.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from . import keycodes, protocol

_MODIFIER_ORDER = ["CTRL", "SHIFT", "ALT", "GUI"]


class KeySlotWidget(QWidget):
    """Uma linha do editor: checkboxes de modificador + combo de tecla."""

    def __init__(self, logical_id: int, parent: QWidget | None = None):
        super().__init__(parent)
        self.logical_id = logical_id

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel(f"Tecla {logical_id + 1}:"))

        self._modifier_checks: dict[str, QCheckBox] = {}
        for name in _MODIFIER_ORDER:
            checkbox = QCheckBox(name)
            self._modifier_checks[name] = checkbox
            layout.addWidget(checkbox)

        self._key_combo = QComboBox()
        self._key_combo.addItem("(nao mapeada)")
        self._key_combo.addItems(keycodes.all_key_names())
        layout.addWidget(self._key_combo, stretch=1)

    def set_action(self, action: protocol.KeyAction) -> None:
        for name, checkbox in self._modifier_checks.items():
            bit = protocol.NAME_TO_MODIFIER[name]
            checkbox.setChecked(bool(action.modifiers & bit))

        if action.keycode == 0:
            self._key_combo.setCurrentIndex(0)
            return

        name = keycodes.name_for_keycode(action.keycode)
        index = self._key_combo.findText(name)
        self._key_combo.setCurrentIndex(index if index >= 0 else 0)

    def get_action(self) -> protocol.KeyAction:
        if self._key_combo.currentIndex() == 0:
            return protocol.KeyAction(protocol.MOD_NONE, 0)

        modifier_names = [name for name, checkbox in self._modifier_checks.items() if checkbox.isChecked()]
        keycode = keycodes.keycode_for_name(self._key_combo.currentText())
        return protocol.KeyAction.from_modifier_names(modifier_names, keycode)


class ProfileEditorWidget(QWidget):
    """Editor completo de um perfil: nome + `MAX_KEYS_PER_PROFILE` slots."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Nome do perfil:"))
        self._name_edit = QLineEdit()
        name_row.addWidget(self._name_edit, stretch=1)
        layout.addLayout(name_row)

        keys_group = QGroupBox("Mapeamento de teclas")
        keys_layout = QGridLayout(keys_group)
        self._slots: list[KeySlotWidget] = []
        for i in range(protocol.MAX_KEYS_PER_PROFILE):
            slot = KeySlotWidget(i)
            self._slots.append(slot)
            keys_layout.addWidget(slot, i, 0)
        layout.addWidget(keys_group)

    def set_profile(self, profile: protocol.Profile) -> None:
        self._name_edit.setText(profile.name)
        for slot, action in zip(self._slots, profile.keys):
            slot.set_action(action)

    def get_profile(self) -> protocol.Profile:
        keys = [slot.get_action() for slot in self._slots]
        return protocol.Profile(name=self._name_edit.text(), keys=keys)
