import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from scipy.stats import shapiro, norm
from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
from statsmodels.stats.stattools import durbin_watson
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tools.tools import add_constant

# A little bit of a nice python implementation of regression diagnostics
# Taken from https://www.statsmodels.org/dev/examples/notebooks/generated/linear_regression_diagnostics_plots.html

# base code
import seaborn as sns
import statsmodels
from statsmodels.tools.tools import maybe_unwrap_results
from statsmodels.graphics.gofplots import ProbPlot
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Type

style_talk = 'seaborn-talk'  # refer to plt.style.available


class LinearRegDiagnostic():
    """
    Diagnostic plots to identify potential problems in a linear regression fit.
    Mainly,
        a. non-linearity of data
        b. Correlation of error terms
        c. non-constant variance
        d. outliers
        e. high-leverage points
        f. collinearity

    Authors:
        Prajwal Kafle (p33ajkafle@gmail.com, where 3 = r)
        Does not come with any sort of warranty.
        Please test the code one your end before using.

        Matt Spinelli (m3spinelli@gmail.com, where 3 = r)
        (1) Fixed incorrect annotation of the top most extreme residuals in
            the Residuals vs Fitted and, especially, the Normal Q-Q plots.
        (2) Changed Residuals vs Leverage plot to match closer the y-axis
            range shown in the equivalent plot in the R package ggfortify.
        (3) Added horizontal line at y=0 in Residuals vs Leverage plot to
            match the plots in R package ggfortify and base R.
        (4) Added option for placing a vertical guideline on the Residuals
            vs Leverage plot using the rule of thumb of h = 2p/n to denote
            high leverage (high_leverage_threshold=True).
        (5) Added two more ways to compute the Cook's Distance (D) threshold:
            * 'baseR': D > 1 and D > 0.5 (default)
            * 'convention': D > 4/n
            * 'dof': D > 4 / (n - k - 1)
        (6) Fixed class name to conform to Pascal casing convention
        (7) Fixed Residuals vs Leverage legend to work with loc='best'
    """

    def __init__(self,
                 results: Type[statsmodels.regression.linear_model.RegressionResultsWrapper]) -> None:
        """
        For a linear regression model, generates following diagnostic plots:

        a. residual
        b. qq
        c. scale location and
        d. leverage

        and a table

        e. vif

        Args:
            results (Type[statsmodels.regression.linear_model.RegressionResultsWrapper]):
                must be instance of statsmodels.regression.linear_model object

        Raises:
            TypeError: if instance does not belong to above object

        Example:
        >>> import numpy as np
        >>> import pandas as pd
        >>> import statsmodels.formula.api as smf
        >>> x = np.linspace(-np.pi, np.pi, 100)
        >>> y = 3*x + 8 + np.random.normal(0,1, 100)
        >>> df = pd.DataFrame({'x':x, 'y':y})
        >>> res = smf.ols(formula= "y ~ x", data=df).fit()
        >>> cls = Linear_Reg_Diagnostic(res)
        >>> cls(plot_context="seaborn-v0_8-paper")

        In case you do not need all plots you can also independently make an individual plot/table
        in following ways

        >>> cls = Linear_Reg_Diagnostic(res)
        >>> cls.residual_plot()
        >>> cls.qq_plot()
        >>> cls.scale_location_plot()
        >>> cls.leverage_plot()
        >>> cls.vif_table()
        """

        if isinstance(results, statsmodels.regression.linear_model.RegressionResultsWrapper) is False:
            raise TypeError(
                "result must be instance of statsmodels.regression.linear_model.RegressionResultsWrapper object")

        self.results = maybe_unwrap_results(results)

        self.y_true = self.results.model.endog
        self.y_predict = self.results.fittedvalues
        self.xvar = self.results.model.exog
        self.xvar_names = self.results.model.exog_names

        self.residual = np.array(self.results.resid)
        influence = self.results.get_influence()
        self.residual_norm = influence.resid_studentized_internal
        self.leverage = influence.hat_matrix_diag
        self.cooks_distance = influence.cooks_distance[0]
        self.nparams = len(self.results.params)
        self.nresids = len(self.residual_norm)

    def __call__(self, plot_context='seaborn-v0_8-paper', **kwargs):
        # print(plt.style.available)
        with plt.style.context(plot_context):
            fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))
            self.residual_plot(ax=ax[0, 0])
            self.qq_plot(ax=ax[0, 1])
            self.scale_location_plot(ax=ax[1, 0])
            self.leverage_plot(
                ax=ax[1, 1],
                high_leverage_threshold=kwargs.get('high_leverage_threshold'),
                cooks_threshold=kwargs.get('cooks_threshold'))
            plt.show()

        return self.vif_table(), fig, ax,

    def residual_plot(self, ax=None):
        """
        Residual vs Fitted Plot

        Graphical tool to identify non-linearity.
        (Roughly) Horizontal red line is an indicator that the residual has a linear pattern
        """
        if ax is None:
            fig, ax = plt.subplots()

        sns.residplot(
            x=self.y_predict,
            y=self.residual,
            lowess=True,
            scatter_kws={'alpha': 0.5},
            line_kws={'color': 'red', 'lw': 1, 'alpha': 0},
            ax=ax)

        # annotations
        residual_abs = np.abs(self.residual)
        abs_resid = np.flip(np.argsort(residual_abs), 0)
        abs_resid_top_3 = abs_resid[:3]
        for i in abs_resid_top_3:
            ax.annotate(
                i,
                xy=(self.y_predict[i], self.residual[i]),
                color='C3')

        ax.set_title('Residuals vs Fitted', fontweight="bold")
        ax.set_xlabel('Fitted values')
        ax.set_ylabel('Residuals')
        return ax

    def qq_plot(self, ax=None):
        """
        Standarized Residual vs Theoretical Quantile plot

        Used to visually check if residuals are normally distributed.
        Points spread along the diagonal line will suggest so.
        """
        if ax is None:
            fig, ax = plt.subplots()

        QQ = ProbPlot(self.residual_norm)
        fig = QQ.qqplot(line='45', alpha=0.5, lw=1, ax=ax)

        # annotations
        abs_norm_resid = np.flip(np.argsort(np.abs(self.residual_norm)), 0)
        abs_norm_resid_top_3 = abs_norm_resid[:3]
        for i, x, y in self.__qq_top_resid(QQ.theoretical_quantiles, abs_norm_resid_top_3):
            ax.annotate(
                i,
                xy=(x, y),
                ha='right',
                color='C3')

        ax.set_title('Normal Q-Q', fontweight="bold")
        ax.set_xlabel('Theoretical Quantiles')
        ax.set_ylabel('Standardized Residuals')
        return ax

    def scale_location_plot(self, ax=None):
        """
        Sqrt(Standarized Residual) vs Fitted values plot

        Used to check homoscedasticity of the residuals.
        Horizontal line will suggest so.
        """
        if ax is None:
            fig, ax = plt.subplots()

        residual_norm_abs_sqrt = np.sqrt(np.abs(self.residual_norm))

        ax.scatter(self.y_predict, residual_norm_abs_sqrt, alpha=0.5)
        sns.regplot(
            x=self.y_predict,
            y=residual_norm_abs_sqrt,
            scatter=False, ci=False,
            lowess=True,
            line_kws={'color': 'red', 'lw': 1, 'alpha': 0.8},
            ax=ax)

        # annotations
        abs_sq_norm_resid = np.flip(np.argsort(residual_norm_abs_sqrt), 0)
        abs_sq_norm_resid_top_3 = abs_sq_norm_resid[:3]
        for i in abs_sq_norm_resid_top_3:
            ax.annotate(
                i,
                xy=(self.y_predict[i], residual_norm_abs_sqrt[i]),
                color='C3')

        ax.set_title('Scale-Location', fontweight="bold")
        ax.set_xlabel('Fitted values')
        ax.set_ylabel(r'$\sqrt{|\mathrm{Standardized\ Residuals}|}$')
        return ax

    def leverage_plot(self, ax=None, high_leverage_threshold=False, cooks_threshold='baseR'):
        """
        Residual vs Leverage plot

        Points falling outside Cook's distance curves are considered observation that can sway the fit
        aka are influential.
        Good to have none outside the curves.
        """
        if ax is None:
            fig, ax = plt.subplots()

        ax.scatter(
            self.leverage,
            self.residual_norm,
            alpha=0.5)

        sns.regplot(
            x=self.leverage,
            y=self.residual_norm,
            scatter=False,
            ci=False,
            lowess=True,
            line_kws={'color': 'red', 'lw': 1, 'alpha': 0.8},
            ax=ax)

        # annotations
        leverage_top_3 = np.flip(np.argsort(self.cooks_distance), 0)[:3]
        for i in leverage_top_3:
            ax.annotate(
                i,
                xy=(self.leverage[i], self.residual_norm[i]),
                color='C3')

        factors = []
        if cooks_threshold == 'baseR' or cooks_threshold is None:
            factors = [1, 0.5]
        elif cooks_threshold == 'convention':
            factors = [4/self.nresids]
        elif cooks_threshold == 'dof':
            factors = [4 / (self.nresids - self.nparams)]
        else:
            raise ValueError(
                "threshold_method must be one of the following: 'convention', 'dof', or 'baseR' (default)")
        for i, factor in enumerate(factors):
            label = "Cook's distance" if i == 0 else None
            xtemp, ytemp = self.__cooks_dist_line(factor)
            ax.plot(xtemp, ytemp, label=label, lw=1.25, ls='--', color='red')
            ax.plot(xtemp, np.negative(ytemp), lw=1.25, ls='--', color='red')

        if high_leverage_threshold:
            high_leverage = 2 * self.nparams / self.nresids
            if max(self.leverage) > high_leverage:
                ax.axvline(high_leverage, label='High leverage',
                           ls='-.', color='purple', lw=1)

        ax.axhline(0, ls='dotted', color='black', lw=1.25)
        ax.set_xlim(0, max(self.leverage)+0.01)
        ax.set_ylim(min(self.residual_norm)-0.1, max(self.residual_norm)+0.1)
        ax.set_title('Residuals vs Leverage', fontweight="bold")
        ax.set_xlabel('Leverage')
        ax.set_ylabel('Standardized Residuals')
        plt.legend(loc='best')
        return ax

    def vif_table(self):
        """
        VIF table

        VIF, the variance inflation factor, is a measure of multicollinearity.
        VIF > 5 for a variable indicates that it is highly collinear with the
        other input variables.
        """
        vif_df = pd.DataFrame()
        vif_df["Features"] = self.xvar_names
        vif_df["VIF Factor"] = [variance_inflation_factor(
            self.xvar, i) for i in range(self.xvar.shape[1])]

        return (vif_df
                .sort_values("VIF Factor")
                .round(2))

    def __cooks_dist_line(self, factor):
        """
        Helper function for plotting Cook's distance curves
        """
        p = self.nparams
        def formula(x): return np.sqrt((factor * p * (1 - x)) / x)
        x = np.linspace(0.001, max(self.leverage), 50)
        y = formula(x)
        return x, y

    def __qq_top_resid(self, quantiles, top_residual_indices):
        """
        Helper generator function yielding the index and coordinates
        """
        offset = 0
        quant_index = 0
        previous_is_negative = None
        for resid_index in top_residual_indices:
            y = self.residual_norm[resid_index]
            is_negative = y < 0
            if previous_is_negative == None or previous_is_negative == is_negative:
                offset += 1
            else:
                quant_index -= offset
            x = quantiles[quant_index] if is_negative else np.flip(quantiles, 0)[
                quant_index]
            quant_index += 1
            previous_is_negative = is_negative
            yield resid_index, x, y

# ---------- Helpers to be robust across .fit() and .fit_regularized() ----------


def _has(obj, name):
    return hasattr(obj, name)


def _get_model(obj):
    return getattr(obj, "model", None)


def _get_params(obj):
    return getattr(obj, "params", None)


def _ensure_2d(a):
    a = np.asarray(a)
    return a[:, None] if a.ndim == 1 else a


def _get_exog(results, data_, features):
    m = _get_model(results)
    if m is not None and _has(m, "exog") and m.exog is not None:
        return _ensure_2d(m.exog)
    return _ensure_2d(np.asarray(data_[features]))


def _get_endog(results, data_, y_col="y"):
    m = _get_model(results)
    if m is not None and _has(m, "endog") and m.endog is not None:
        return np.asarray(m.endog).ravel()
    return np.asarray(data_[y_col]).ravel()


def _predict_from_results(results, X=None):
    if _has(results, "fittedvalues") and results.fittedvalues is not None:
        return np.asarray(results.fittedvalues).ravel()

    if _has(results, "predict"):
        try:
            pv = results.predict() if X is None else results.predict(X)
            return np.asarray(pv).ravel()
        except Exception:
            pass

    m = _get_model(results)
    params = _get_params(results)
    if m is not None and params is not None:
        try:
            if X is not None:
                return np.asarray(m.predict(params, exog=X)).ravel()
            else:
                return np.asarray(m.predict(params)).ravel()
        except Exception:
            pass

    if X is not None and params is not None:
        beta = np.asarray(params).ravel()
        X2 = _ensure_2d(X)
        return np.asarray(X2 @ beta).ravel()

    raise RuntimeError("Cannot compute predictions from provided results.")


def _get_residuals(results, data_, features, y_col="y"):
    if _has(results, "resid") and results.resid is not None:
        r = np.asarray(results.resid).ravel()
        if np.all(np.isfinite(r)):
            return r
    y = _get_endog(results, data_, y_col=y_col)
    X = _get_exog(results, data_, features)
    yhat = _predict_from_results(results, X=X)
    return y - yhat


def _make_linear_diag(results):
    if "LinearRegDiagnostic" not in globals():
        return None
    try:
        return LinearRegDiagnostic(results)
    except Exception:
        return None


def _exog_for_bp(results, data_, features):
    exog = _get_exog(results, data_, features)
    try:
        exog = add_constant(exog, has_constant='add')
    except Exception:
        # naive constant prepend if add_constant is problematic
        if exog.ndim == 1:
            exog = exog[:, None]
        if not np.allclose(exog[:, 0], 1.0):
            exog = np.column_stack([np.ones(exog.shape[0]), exog])
    return exog

# ---------- Tests (robust across .fit() and .fit_regularized()) ----------


def test_linearity(model, data_, features, model_name="Model", y_col="y"):
    print("TEST LINEARITY")
    resid = _get_residuals(model, data_, features, y_col=y_col)
    diag = _make_linear_diag(model)

    # Dependent vs independent variables
    number_of_rows = (len(features) + 4) // 5
    y_size = 4 * number_of_rows
    fig, axes = plt.subplots(number_of_rows, 5, figsize=(20, y_size))
    axes = axes.flatten()

    for i, feature in enumerate(features):
        axes[i].scatter(data_[feature], data_[y_col],
                        alpha=0.5, s=20, color='darkblue')
        sns.regplot(x=data_[feature], y=data_[y_col], scatter=False, lowess=True,
                    line_kws={'lw': 2, 'alpha': 0.9}, ax=axes[i])
        axes[i].set_xlabel(feature, fontsize=11)
        axes[i].set_ylabel(y_col, fontsize=11)
        axes[i].set_title(f'{y_col} vs {feature}',
                          fontsize=12, fontweight='bold')
        axes[i].grid(alpha=0.3)
    for j in range(len(features), len(axes)):
        axes[j].axis('off')
    plt.suptitle(f'{model_name}: Dependent vs Independent Variables',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.show()

    print("Interpretation:")
    print("  - LOWESS line shows the trend between each feature and target")
    print("  - Linear trend = good; curved pattern = potential non-linearity")
    print()

    # Residuals vs each independent variable
    fig, axes = plt.subplots(number_of_rows, 5, figsize=(20, y_size))
    axes = axes.flatten()
    for i, feature in enumerate(features):
        axes[i].scatter(data_[feature], resid, alpha=0.5, s=20)
        axes[i].axhline(y=0, color='r', linestyle='--', linewidth=1)
        sns.regplot(x=data_[feature], y=resid, scatter=False, lowess=True,
                    line_kws={'lw': 1.5}, ax=axes[i])
        axes[i].set_xlabel(feature, fontsize=11)
        axes[i].set_ylabel('Residuals', fontsize=11)
        axes[i].set_title(
            f'Residuals vs {feature}', fontsize=12, fontweight='bold')
        axes[i].grid(alpha=0.3)
    for j in range(len(features), len(axes)):
        axes[j].axis('off')
    plt.suptitle(f'{model_name}: Residuals vs Independent Variables',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.show()

    print("Interpretation:")
    print("  - Points should be randomly scattered around y=0; no patterns")
    print("  - Curves = non-linearity; funnel = heteroscedasticity")
    print("------------------------------------------------")


def test_homoscedacity(model, name, data_=None, features=None, y_col="y"):
    print("TEST HOMOSCEDASTICITY")
    if data_ is None or features is None:
        # minimal fallbacks; may not have a constant -> fix below
        data_ = {} if data_ is None else data_
        features = [] if features is None else features
    exog = _exog_for_bp(model, data_, features)
    resid = _get_residuals(model, data_, features, y_col=y_col)
    stat, pval, _, _ = het_breuschpagan(resid, exog)
    print(
        f"Breusch–Pagan LM p-value for {name}: {pval:.4g} (LM stat={stat:.3f})")
    print("------------------------------------------------")
    return pval


def test_independence_of_errors(model, name, data_, features, y_col="y", lb_lags=(10, 20, 40)):
    print("TEST INDEPENDENCE OF ERRORS")
    resid = _get_residuals(model, data_, features, y_col=y_col)
    dw_stat = durbin_watson(resid)
    print(f"Durbin–Watson statistic for {name}: {dw_stat:.3f}")

    lb = acorr_ljungbox(resid, lags=list(lb_lags), return_df=True)
    print(f"Ljung–Box test results for {name} (lags {list(lb_lags)}):")
    print(lb)

    fig, ax = plt.subplots(figsize=(10, 4))
    plot_acf(resid, lags=max(lb_lags), ax=ax)
    plt.title('Autocorrelation Function (ACF) of Residuals - ' + name)
    plt.xlabel('Lag')
    plt.ylabel('Autocorrelation')
    plt.tight_layout()
    plt.show()
    print("------------------------------------------------")


def test_normality_of_errors(model, name, data_, features, y_col="y"):
    print("TEST NORMALITY OF ERRORS")
    resid = _get_residuals(model, data_, features, y_col=y_col)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    diag = _make_linear_diag(model)
    if diag is not None:
        diag.residual_plot(ax=axes[0])
        axes[0].set_title(name)
        diag.qq_plot(ax=axes[1])
        axes[1].set_title('Q–Q Plot (' + name + ')')
    else:
        fitted = _predict_from_results(
            model, X=_get_exog(model, data_, features))
        axes[0].scatter(fitted, resid, alpha=0.5, s=20)
        sns.regplot(x=fitted, y=resid, scatter=False,
                    lowess=True, line_kws={'lw': 2}, ax=axes[0])
        axes[0].axhline(0, ls='--', lw=1, c='r')
        axes[0].set_title(f'Residuals vs Fitted ({name})')
        axes[0].set_xlabel('Fitted')
        axes[0].set_ylabel('Residuals')
        import statsmodels.api as sm
        sm.ProbPlot(resid, fit=True).qqplot(ax=axes[1], line='45')
        axes[1].set_title('Q–Q Plot (' + name + ')')
    plt.tight_layout()
    plt.show()

    # Histogram with normal overlay
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(resid, bins=50, density=True, alpha=0.7, edgecolor='black')
    mu, sigma = resid.mean(), resid.std()
    x = np.linspace(resid.min(), resid.max(), 200)
    ax.plot(x, norm.pdf(x, mu, sigma), '-',
            linewidth=2, label='Normal approx.')
    ax.set_xlabel('Residuals')
    ax.set_ylabel('Density')
    ax.set_title('Histogram of Residuals (' + name + ')')
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    stat, pval = shapiro(resid)
    print(f"Shapiro–Wilk test for {name}: W={stat:.4f}, p-value={pval:.4g}")
    print("------------------------------------------------")


def test_multicollinearity(model, name, variables, data_):
    print("TEST MULTICOLLINEARITY")
    correlation_matrix = data_[variables].corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True,
                cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Correlation Matrix - ' + name)
    plt.tight_layout()
    plt.show()

    diag = _make_linear_diag(model)
    if diag is not None:
        print("Variance Inflation Factor (VIF):")
        print(diag.vif_table())
    else:
        import pandas as pd
        from statsmodels.regression.linear_model import OLS
        X = add_constant(data_[variables].values, has_constant='add')
        vif_rows = []
        for j in range(1, X.shape[1]):  # skip constant
            yj = X[:, j]
            X_others = np.delete(X, j, axis=1)
            r2 = OLS(yj, X_others).fit().rsquared
            vif = np.inf if (1 - r2) <= 1e-12 else 1.0 / (1.0 - r2)
            vif_rows.append((variables[j-1], vif))
        print("Variance Inflation Factor (manual):")
        print(pd.DataFrame(vif_rows, columns=["variable", "VIF"]))
    print("------------------------------------------------")


def perform_all_tests(model, data_, features, model_name="Model", y_col="y"):
    data_copy = data_.copy()
    test_linearity(model, data_copy, features, model_name, y_col=y_col)
    test_homoscedacity(model, model_name, data_=data_copy,
                       features=features, y_col=y_col)
    test_independence_of_errors(
        model, model_name, data_copy, features, y_col=y_col)
    test_normality_of_errors(
        model, model_name, data_copy, features, y_col=y_col)
    test_multicollinearity(model, model_name, features, data_copy)


np.random.seed(42)
