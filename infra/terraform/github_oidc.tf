# -----------------------------------------------------------------------------
# GitHub Actions OIDC
# -----------------------------------------------------------------------------

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}

data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:Yhodiux/aws-retail-data-platform:ref:refs/heads/main"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  name = "olist-github-actions-${var.environment}"

  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
}

# -----------------------------------------------------------------------------
# Terraform Remote State Access
# -----------------------------------------------------------------------------

data "aws_iam_policy_document" "github_actions_terraform_state" {
  statement {
    sid = "ListTerraformStateBucket"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::olist-retail-data-dev-us-east-1-793a6f"
    ]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "terraform/dev/*"
      ]
    }
  }

  statement {
    sid = "ManageTerraformState"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "arn:aws:s3:::olist-retail-data-dev-us-east-1-793a6f/terraform/dev/terraform.tfstate",
      "arn:aws:s3:::olist-retail-data-dev-us-east-1-793a6f/terraform/dev/terraform.tfstate.tflock"
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_terraform_state" {
  name   = "olist-github-actions-terraform-state"
  role   = aws_iam_role.github_actions.name
  policy = data.aws_iam_policy_document.github_actions_terraform_state.json
}

resource "aws_iam_role_policy_attachment" "github_actions_read_only" {
  role       = aws_iam_role.github_actions.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}