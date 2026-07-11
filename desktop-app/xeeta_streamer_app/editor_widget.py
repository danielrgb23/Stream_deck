"""Editor de mapeamento de teclas (specs feature-button-mapping, target-os-shortcuts).

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

from . import keycodes, named_actions, protocol

_MODIFIER_ORDER = ["CTRL", "SHIFT", "ALT", "GUI"]
_MANUAL_LABEL = "(manual)"
_TARGET_OS_LABELS = {
    protocol.TARGET_OS_WINDOWS: "Windows",
    protocol.TARGET_OS_MAC: "Mac",
}


class KeySlotWidget(QWidget):
    """Uma linha do editor: ação nomeada + checkboxes de modificador + combo de tecla.

    A ação nomeada é só um atalho para preencher modificadores/tecla — editar
    qualquer um dos dois manualmente depois desmarca a ação nomeada (a tecla
    volta a ser tratada como mapeamento manual, spec target-os-shortcuts).
    """

    def __init__(self, logical_id: int, target_os: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.logical_id = logical_id
        self._target_os = target_os
        self._named_action: str | None = None
        self._updating = False  # guarda contra loop de feedback ao setar campos programaticamente

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel(f"Tecla {logical_id + 1}:"))

        self._named_action_combo = QComboBox()
        self._named_action_combo.addItem(_MANUAL_LABEL, None)
        for name in named_actions.action_names():
            self._named_action_combo.addItem(named_actions.DISPLAY_NAMES[name], name)
        self._named_action_combo.currentIndexChanged.connect(self._handle_named_action_changed)
        layout.addWidget(self._named_action_combo)

        self._modifier_checks: dict[str, QCheckBox] = {}
        for name in _MODIFIER_ORDER:
            checkbox = QCheckBox(name)
            checkbox.stateChanged.connect(self._handle_manual_edit)
            self._modifier_checks[name] = checkbox
            layout.addWidget(checkbox)

        self._key_combo = QComboBox()
        self._key_combo.addItem("(nao mapeada)")
        self._key_combo.addItems(keycodes.all_key_names())
        self._key_combo.currentIndexChanged.connect(self._handle_manual_edit)
        layout.addWidget(self._key_combo, stretch=1)

    def set_target_os(self, target_os: str) -> None:
        """Troca o SO-alvo. Se a tecla veio de uma ação nomeada, re-resolve
        para o novo SO; se foi mapeada manualmente, não mexe em nada (spec
        target-os-shortcuts: trocar o SO-alvo não sobrescreve edição manual)."""
        self._target_os = target_os
        if self._named_action is not None:
            self._apply_named_action(self._named_action)

    def set_action(self, action: protocol.KeyAction) -> None:
        self._updating = True
        try:
            self._set_fields(action)
            self._named_action = action.named_action
            index = self._named_action_combo.findData(self._named_action)
            self._named_action_combo.setCurrentIndex(index if index >= 0 else 0)
        finally:
            self._updating = False

    def get_action(self) -> protocol.KeyAction:
        if self._key_combo.currentIndex() == 0:
            return protocol.KeyAction(protocol.MOD_NONE, 0, named_action=self._named_action)

        modifier_names = [name for name, checkbox in self._modifier_checks.items() if checkbox.isChecked()]
        keycode = keycodes.keycode_for_name(self._key_combo.currentText())
        return protocol.KeyAction.from_modifier_names(modifier_names, keycode, named_action=self._named_action)

    def _set_fields(self, action: protocol.KeyAction) -> None:
        for name, checkbox in self._modifier_checks.items():
            bit = protocol.NAME_TO_MODIFIER[name]
            checkbox.setChecked(bool(action.modifiers & bit))

        if action.keycode == 0:
            self._key_combo.setCurrentIndex(0)
            return

        name = keycodes.name_for_keycode(action.keycode)
        index = self._key_combo.findText(name)
        self._key_combo.setCurrentIndex(index if index >= 0 else 0)

    def _apply_named_action(self, action_name: str) -> None:
        action = named_actions.resolve(action_name, self._target_os)
        self._updating = True
        try:
            self._set_fields(action)
        finally:
            self._updating = False
        self._named_action = action_name

    def _handle_named_action_changed(self, _index: int) -> None:
        if self._updating:
            return

        action_name = self._named_action_combo.currentData()
        if action_name is None:
            self._named_action = None
            return

        self._apply_named_action(action_name)

    def _handle_manual_edit(self, *_args) -> None:
        if self._updating:
            return

        # Usuario tocou um checkbox ou o combo de tecla diretamente: a partir
        # de agora esta tecla e mapeamento manual, nao mais ligada a acao
        # nomeada nenhuma.
        self._named_action = None
        self._updating = True
        try:
            self._named_action_combo.setCurrentIndex(0)
        finally:
            self._updating = False


class ProfileEditorWidget(QWidget):
    """Editor completo de um perfil: nome + SO-alvo + `MAX_KEYS_PER_PROFILE` slots."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self._target_os = protocol.DEFAULT_TARGET_OS

        layout = QVBoxLayout(self)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Nome do perfil:"))
        self._name_edit = QLineEdit()
        name_row.addWidget(self._name_edit, stretch=1)

        name_row.addWidget(QLabel("Sistema-alvo:"))
        self._target_os_combo = QComboBox()
        for target_os in protocol.TARGET_OS_CHOICES:
            self._target_os_combo.addItem(_TARGET_OS_LABELS[target_os], target_os)
        self._target_os_combo.currentIndexChanged.connect(self._handle_target_os_changed)
        name_row.addWidget(self._target_os_combo)

        layout.addLayout(name_row)

        keys_group = QGroupBox("Mapeamento de teclas")
        keys_layout = QGridLayout(keys_group)
        self._slots: list[KeySlotWidget] = []
        for i in range(protocol.MAX_KEYS_PER_PROFILE):
            slot = KeySlotWidget(i, self._target_os)
            self._slots.append(slot)
            keys_layout.addWidget(slot, i, 0)
        layout.addWidget(keys_group)

    def _handle_target_os_changed(self, _index: int) -> None:
        self._target_os = self._target_os_combo.currentData()
        for slot in self._slots:
            slot.set_target_os(self._target_os)

    def set_profile(self, profile: protocol.Profile) -> None:
        self._name_edit.setText(profile.name)

        self._target_os = profile.target_os
        index = self._target_os_combo.findData(profile.target_os)
        self._target_os_combo.setCurrentIndex(index if index >= 0 else 0)

        for slot, action in zip(self._slots, profile.keys):
            slot.set_target_os(self._target_os)
            slot.set_action(action)

    def get_profile(self) -> protocol.Profile:
        keys = [slot.get_action() for slot in self._slots]
        return protocol.Profile(name=self._name_edit.text(), keys=keys, target_os=self._target_os)
