import pytest

from tools.check_publish import PublicationGateError, evaluate


def publication():
    return {
        "source_permissions_resolved": True,
        "package_ownership_verified": False,
        "trusted_publishing_configured": False,
        "bootstrap_publish": {
            "testpypi": {
                "reacli": {"allowed": True},
                "reaper-parser": {"allowed": False},
            }
        },
    }


def test_normal_mode_keeps_global_prerequisite_gate():
    with pytest.raises(
        PublicationGateError,
        match="package_ownership_verified, trusted_publishing_configured",
    ):
        evaluate(publication(), target="testpypi", package="reacli")


def test_testpypi_bootstrap_allows_manifest_authorized_package():
    evaluate(
        publication(),
        target="testpypi",
        package="reacli",
        mode="testpypi-bootstrap",
    )


def test_testpypi_bootstrap_rejects_unregistered_package():
    with pytest.raises(
        PublicationGateError, match="TestPyPI bootstrap not authorized for package"
    ):
        evaluate(
            publication(),
            target="testpypi",
            package="reaper-parser",
            mode="testpypi-bootstrap",
        )


def test_testpypi_bootstrap_cannot_target_pypi():
    with pytest.raises(
        PublicationGateError, match="TestPyPI bootstrap requires TARGET=testpypi"
    ):
        evaluate(
            publication(),
            target="pypi",
            package="reacli",
            mode="testpypi-bootstrap",
        )


def test_normal_pypi_requires_ecosystem_tag_after_prerequisites_pass():
    record = publication()
    record.update(
        package_ownership_verified=True,
        trusted_publishing_configured=True,
    )
    with pytest.raises(
        PublicationGateError, match="Production requires an ecosystem-v release tag"
    ):
        evaluate(
            record,
            target="pypi",
            package="reacli",
            ref_type="branch",
            ref_name="main",
        )
