"""
MineGuard AI — Explainable AI Module

Provides:
1. Global feature importance
2. Local explanations for individual predictions
3. Support for Random Forest and Logistic Regression
"""

import numpy as np
import pandas as pd


class MineGuardXAI:
    """
    Explainability engine for MineGuard AI models.
    """

    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = list(feature_names)

    # ========================================================
    # Global explanation
    # ========================================================

    def global_feature_importance(self, top_n=10):
        """
        Return globally important features.

        Random Forest:
            Uses feature_importances_

        Logistic Regression:
            Uses absolute coefficient magnitude.
        """

        if hasattr(self.model, "feature_importances_"):
            importance = np.asarray(
                self.model.feature_importances_
            )

        elif hasattr(self.model, "coef_"):
            coefficients = np.asarray(
                self.model.coef_
            )

            if coefficients.ndim == 2:
                importance = np.abs(coefficients[0])
            else:
                importance = np.abs(coefficients)

        else:
            raise ValueError(
                "Model does not expose feature importance "
                "or coefficients."
            )

        if len(importance) != len(self.feature_names):
            raise ValueError(
                "Number of feature importance values does not "
                "match number of feature names."
            )

        result = pd.DataFrame({
            "feature": self.feature_names,
            "importance": importance
        })

        result = result.sort_values(
            "importance",
            ascending=False
        )

        return result.head(top_n).reset_index(drop=True)

    # ========================================================
    # Local explanation
    # ========================================================

    def explain_prediction(self, X):
        """
        Explain one or more individual predictions.

        For Logistic Regression:
            contribution = transformed_feature * coefficient

        For tree-based models:
            returns feature importance as a global proxy.
        """

        X_array = np.asarray(X)

        if X_array.ndim == 1:
            X_array = X_array.reshape(1, -1)

        probabilities = self.model.predict_proba(
            X_array
        )[:, 1]

        explanations = []

        for row_index, row in enumerate(X_array):

            # -----------------------------------------------
            # Logistic Regression
            # -----------------------------------------------

            if hasattr(self.model, "coef_"):

                coefficients = np.asarray(
                    self.model.coef_[0]
                )

                contributions = row * coefficients

                feature_contributions = []

                for feature, value, contribution in zip(
                    self.feature_names,
                    row,
                    contributions
                ):
                    feature_contributions.append({
                        "feature": feature,
                        "value": float(value),
                        "contribution": float(contribution),
                        "direction": (
                            "increases_risk"
                            if contribution > 0
                            else "decreases_risk"
                        )
                    })

                feature_contributions.sort(
                    key=lambda x: abs(
                        x["contribution"]
                    ),
                    reverse=True
                )

            # -----------------------------------------------
            # Tree model
            # -----------------------------------------------

            elif hasattr(
                self.model,
                "feature_importances_"
            ):

                importances = np.asarray(
                    self.model.feature_importances_
                )

                feature_contributions = []

                for feature, value, importance in zip(
                    self.feature_names,
                    row,
                    importances
                ):
                    feature_contributions.append({
                        "feature": feature,
                        "value": float(value),
                        "importance": float(importance),
                        "direction": "model_global_importance"
                    })

                feature_contributions.sort(
                    key=lambda x: x["importance"],
                    reverse=True
                )

            else:
                raise ValueError(
                    "Unsupported model for XAI."
                )

            explanations.append({
                "prediction_probability": float(
                    probabilities[row_index]
                ),
                "top_contributors":
                    feature_contributions[:10]
            })

        return explanations