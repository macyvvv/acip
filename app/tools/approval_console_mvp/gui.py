from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from .service import ApprovalConsoleService, ApprovalScope


class ApprovalConsoleGUI:
    def __init__(self, root: tk.Tk, repo_root: str | Path = ".") -> None:
        self.root = root
        self.service = ApprovalConsoleService(repo_root)
        self.scopes: list[ApprovalScope] = []
        self.selected_scope: ApprovalScope | None = None
        self.last_result = None

        self.root.title("Approval Console MVP")
        self.root.geometry("860x520")

        self.scope_list = tk.Listbox(root, height=8)
        self.scope_list.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
        self.scope_list.bind("<<ListboxSelect>>", self._on_select)

        self.refresh_button = tk.Button(root, text="Refresh", command=self.refresh)
        self.refresh_button.grid(row=1, column=0, sticky="ew", padx=8, pady=4)

        self.approve_button = tk.Button(root, text="Approve", command=self.approve_selected)
        self.approve_button.grid(row=1, column=1, sticky="ew", padx=8, pady=4)

        self.evaluate_button = tk.Button(root, text="Evaluate", command=self.evaluate)
        self.evaluate_button.grid(row=1, column=2, sticky="ew", padx=8, pady=4)

        self.execute_button = tk.Button(root, text="Run One-Shot", command=self.execute)
        self.execute_button.grid(row=1, column=3, sticky="ew", padx=8, pady=4)

        self.status = tk.Text(root, wrap="word", height=18)
        self.status.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
        self.summary = tk.Label(root, text="", anchor="w", justify="left")
        self.summary.grid(row=3, column=0, columnspan=4, sticky="ew", padx=8, pady=(0, 8))

        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=4)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

        self.refresh()

    def refresh(self) -> None:
        self.scopes = self.service.load_scopes()
        self.scope_list.delete(0, tk.END)
        if not self.scopes:
            self.scope_list.insert(tk.END, "No approval-eligible candidate")
        for scope in self.scopes:
            self.scope_list.insert(
                tk.END,
                f"{scope.scope_type}:{scope.scope_id} | bucket={scope.current_bucket} | fit={scope.execution_fit} | approval={scope.approval_status}",
            )
        self.summary.config(
            text=(
                f"Candidates: {len(self.scopes)}"
                + (
                    " | Recommended next candidate available"
                    if any(scope.approval_ready for scope in self.scopes)
                    else " | Candidate visible, but approval not ready"
                )
            )
        )
        self._update_buttons()
        self._render()

    def _selected(self) -> ApprovalScope | None:
        selection = self.scope_list.curselection()
        if not selection:
            return None
        index = selection[0]
        if index >= len(self.scopes):
            return None
        return self.scopes[index]

    def _on_select(self, _event: object) -> None:
        self.selected_scope = self._selected()
        self._update_buttons()
        self._render()

    def approve_selected(self) -> None:
        scope = self._selected()
        if scope is None:
            messagebox.showwarning("Approval Console", "Select exactly one scope.")
            return
        self.selected_scope = scope
        self.last_result = self.service.approve_scope(scope, approved_by="human", reason="Approved from Approval Console MVP.")
        self._update_buttons()
        self._render()

    def evaluate(self) -> None:
        self.last_result = self.service.evaluate_approval()
        self._update_buttons()
        self._render()

    def execute(self) -> None:
        scope = self._selected()
        if scope is None:
            messagebox.showwarning("Approval Console", "Select exactly one scope.")
            return
        self.selected_scope = scope
        self.last_result = self.service.run_one_shot_execution()
        self._update_buttons()
        self._render()

    def _render(self) -> None:
        self.status.delete("1.0", tk.END)
        self.status.insert(tk.END, self.service.render_status(self.selected_scope, self.last_result))
        self._update_buttons()

    def _update_buttons(self) -> None:
        selected = self.selected_scope
        approval_ready = bool(selected and selected.approval_ready)
        has_selection = selected is not None
        self.approve_button.config(state=tk.NORMAL if approval_ready else tk.DISABLED)
        self.evaluate_button.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.execute_button.config(state=tk.NORMAL if approval_ready else tk.DISABLED)


def launch(repo_root: str | Path = ".") -> None:
    root = tk.Tk()
    ApprovalConsoleGUI(root, repo_root=repo_root)
    root.mainloop()
