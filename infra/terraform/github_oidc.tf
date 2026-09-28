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

# -----------------------------------------------------------------------------
# GitHub Actions - Terraform deployment permissions
# -----------------------------------------------------------------------------

data "aws_iam_policy_document" "github_actions_deploy" {

  statement {
    sid = "DeployS3"

    actions = [
      "s3:CreateBucket",
      "s3:DeleteBucket",
      "s3:PutBucketVersioning",
      "s3:PutEncryptionConfiguration",
      "s3:PutBucketPublicAccessBlock",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      aws_s3_bucket.data.arn,
      "${aws_s3_bucket.data.arn}/*"
    ]
  }

  statement {
    sid = "DeployGlue"

    actions = [
      "glue:CreateDatabase",
      "glue:UpdateDatabase",
      "glue:DeleteDatabase",
      "glue:CreateJob",
      "glue:UpdateJob",
      "glue:DeleteJob",
      "glue:CreateCrawler",
      "glue:UpdateCrawler",
      "glue:DeleteCrawler",
      "glue:CreateWorkflow",
      "glue:UpdateWorkflow",
      "glue:DeleteWorkflow",
      "glue:CreateTrigger",
      "glue:UpdateTrigger",
      "glue:DeleteTrigger"
    ]

    resources = ["*"]
  }

  statement {
    sid = "DeployLambda"

    actions = [
      "lambda:CreateFunction",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
      "lambda:DeleteFunction",
      "lambda:AddPermission",
      "lambda:RemovePermission",
      "lambda:TagResource",
      "lambda:UntagResource"
    ]

    resources = ["*"]
  }

  statement {
    sid = "DeployApiGateway"

    actions = [
      "apigateway:POST",
      "apigateway:PUT",
      "apigateway:PATCH",
      "apigateway:DELETE"
    ]

    resources = ["*"]
  }

  statement {
    sid = "DeployMonitoring"

    actions = [
      "sns:CreateTopic",
      "sns:DeleteTopic",
      "sns:SetTopicAttributes",
      "events:PutRule",
      "events:DeleteRule",
      "events:PutTargets",
      "events:RemoveTargets"
    ]

    resources = ["*"]
  }

  statement {
    sid = "ManageProjectIam"

    actions = [
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:UpdateAssumeRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:TagRole",
      "iam:UntagRole"
    ]

    resources = [
      "arn:aws:iam::746552104319:role/olist-*"
    ]
  }

  statement {
    sid = "PassProjectRoles"

    actions = [
      "iam:PassRole"
    ]

    resources = [
      "arn:aws:iam::746552104319:role/olist-*",
      data.aws_iam_role.glue.arn
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_deploy" {
  name   = "olist-github-actions-deploy"
  role   = aws_iam_role.github_actions.name
  policy = data.aws_iam_policy_document.github_actions_deploy.json
}