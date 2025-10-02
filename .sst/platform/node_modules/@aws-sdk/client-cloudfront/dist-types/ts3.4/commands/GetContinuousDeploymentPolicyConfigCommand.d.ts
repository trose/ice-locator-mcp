import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  GetContinuousDeploymentPolicyConfigRequest,
  GetContinuousDeploymentPolicyConfigResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface GetContinuousDeploymentPolicyConfigCommandInput
  extends GetContinuousDeploymentPolicyConfigRequest {}
export interface GetContinuousDeploymentPolicyConfigCommandOutput
  extends GetContinuousDeploymentPolicyConfigResult,
    __MetadataBearer {}
export declare class GetContinuousDeploymentPolicyConfigCommand extends $Command<
  GetContinuousDeploymentPolicyConfigCommandInput,
  GetContinuousDeploymentPolicyConfigCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: GetContinuousDeploymentPolicyConfigCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: GetContinuousDeploymentPolicyConfigCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    GetContinuousDeploymentPolicyConfigCommandInput,
    GetContinuousDeploymentPolicyConfigCommandOutput
  >;
  private serialize;
  private deserialize;
}
